from decimal import Decimal
from django.db import transaction
from django.db.models import Sum, Count, Q
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from .models import (
    Match,
    Innings,
    BallByBall,
    PointsTable,
    CollegeRegistration,
    CollegeTeamMember,
)


class ScoringEngineService:

    @staticmethod
    def get_current_over_and_ball(innings):
        """
        Calculates the current over and next legal ball number in the innings.
        """
        legal_balls_count = BallByBall.objects.filter(
            innings=innings,
            extra_type__in=['none', 'bye', 'leg_bye', 'penalty']
        ).count()

        completed_overs = legal_balls_count // 6
        current_ball_in_over = (legal_balls_count % 6) + 1

        return completed_overs, current_ball_in_over, legal_balls_count

    @classmethod
    def generate_ball_commentary(cls, striker_name, bowler_name, runs, extra_type, is_wicket, wicket_type, fielder_name=None):
        """
        Generates contextual cricket commentary automatically if manual text is omitted.
        """
        if is_wicket:
            if wicket_type == 'bowled':
                return f"OUT! Clean bowled! {bowler_name} rattles the stumps, {striker_name} departs!"
            elif wicket_type == 'caught':
                f_name = fielder_name if fielder_name else "the fielder"
                return f"OUT! In the air and taken! {striker_name} caught by {f_name} off {bowler_name}."
            elif wicket_type == 'lbw':
                return f"OUT! Huge appeal for LBW and the umpire raises the finger! {striker_name} out LBW."
            elif wicket_type == 'run_out':
                return f"OUT! Run out! Direct hit from {fielder_name or 'the fielders'}!"
            elif wicket_type == 'stumped':
                return f"OUT! Stumped! Keeper whips off the bails to dismiss {striker_name}."
            return f"OUT! {striker_name} loses their wicket ({wicket_type}) to {bowler_name}."

        if extra_type == 'wide':
            return f"Wide ball called by the umpire. {bowler_name} sprays it down the leg side."
        elif extra_type == 'no_ball':
            return f"No ball called! Overstepping by {bowler_name}. Free hit coming up!"
        elif extra_type == 'bye':
            return f"Byes conceded. The batters steal {runs} run(s)."
        elif extra_type == 'leg_bye':
            return f"Leg bye signaled as the ball deflects off the pads for {runs} run(s)."

        if runs == 6:
            return f"SIX! Massive hit from {striker_name}! Lofts {bowler_name} way over the boundary!"
        elif runs == 4:
            return f"FOUR! Cracking shot through the gap! {striker_name} sends {bowler_name} to the fence."
        elif runs == 1:
            return f"Pushed into the gap by {striker_name} for a single."
        elif runs == 2:
            return f"Good running between the wickets, {striker_name} and partner complete two runs."
        elif runs == 3:
            return f"Well placed into deep territory, allowing {striker_name} to pick up three runs."
        else:
            return f"No run. Solid defensive shot from {striker_name} against {bowler_name}."

    @classmethod
    @transaction.atomic
    def process_delivery(cls, innings, data):
        """
        Processes a single ball delivery within an atomic transaction.
        Handles runs, extras, wickets, strike rotation, over changes, and target chasing.
        """
        match = innings.match
        runs_scored = int(data.get('runs_scored', 0))
        extra_type = data.get('extra_type', 'none')
        extra_runs = int(data.get('extra_runs', 0))
        is_wicket = bool(data.get('is_wicket', False))
        wicket_type = data.get('wicket_type', None)
        player_dismissed = data.get('player_dismissed', None)
        fielder_involved = data.get('fielder_involved', None)
        commentary_text = data.get('commentary_text', '')

        striker = data['striker']
        non_striker = data['non_striker']
        bowler = data['bowler']

        # Determine if this delivery counts towards the 6 balls of the over
        is_legal_ball = extra_type not in ['wide', 'no_ball']

        completed_overs, current_ball_in_over, prev_legal_count = cls.get_current_over_and_ball(innings)

        # Auto generate commentary if not provided
        if not commentary_text:
            f_name = fielder_involved.name if fielder_involved else None
            commentary_text = cls.generate_ball_commentary(
                striker_name=striker.name,
                bowler_name=bowler.name,
                runs=runs_scored,
                extra_type=extra_type,
                is_wicket=is_wicket,
                wicket_type=wicket_type,
                fielder_name=f_name
            )

        # 1. Save Ball-by-Ball record
        ball = BallByBall.objects.create(
            innings=innings,
            over_number=completed_overs,
            ball_number=current_ball_in_over if is_legal_ball else max(current_ball_in_over - 1, 0),
            bowler=bowler,
            striker=striker,
            non_striker=non_striker,
            runs_scored=runs_scored,
            is_dot_ball=(runs_scored == 0 and extra_runs == 0 and not is_wicket),
            is_four=(runs_scored == 4),
            is_six=(runs_scored == 6),
            extra_type=extra_type,
            extra_runs=extra_runs,
            is_wicket=is_wicket,
            wicket_type=wicket_type,
            player_dismissed=player_dismissed,
            fielder_involved=fielder_involved,
            commentary_text=commentary_text
        )

        # 2. Update Innings Running Total
        total_ball_runs = runs_scored + extra_runs
        innings.total_runs += total_ball_runs

        if is_wicket and wicket_type != 'retired_hurt':
            innings.total_wickets += 1

        # Calculate new total overs in decimal (e.g. 4.5 -> 4.5, 4.6 -> 5.0)
        new_legal_count = prev_legal_count + (1 if is_legal_ball else 0)
        overs_part = new_legal_count // 6
        balls_part = new_legal_count % 6
        innings.total_overs = Decimal(f"{overs_part}.{balls_part}")
        innings.save()

        # 3. Strike Rotation Logic
        next_striker = striker
        next_non_striker = non_striker
        is_over_complete = False

        # Physical runs (odd numbers swap ends)
        if runs_scored % 2 != 0:
            next_striker, next_non_striker = next_non_striker, next_striker

        # End of over: 6 legal balls completed
        if is_legal_ball and balls_part == 0:
            is_over_complete = True
            # Over change swaps strike ends
            next_striker, next_non_striker = next_non_striker, next_striker

        # If striker got out, caller needs to assign next batsman
        if is_wicket and player_dismissed == striker:
            next_striker = None
        elif is_wicket and player_dismissed == non_striker:
            next_non_striker = None

        # 4. Check Innings & Match Termination
        innings_ended = False
        match_ended = False
        winner = None
        result_desc = ""

        # Condition A: 10 Wickets down or Max Overs reached
        max_overs_reached = (overs_part >= match.total_overs)
        all_out = (innings.total_wickets >= 10)

        if innings.innings_number == 1:
            if max_overs_reached or all_out:
                innings.is_completed = True
                innings.save()
                innings_ended = True
                match.status = 'innings_break'
                match.save(update_fields=['status'])

        elif innings.innings_number == 2:
            # 2nd Innings Target Evaluation
            first_innings = match.innings.filter(innings_number=1).first()
            target = (first_innings.total_runs + 1) if first_innings else 1

            if innings.total_runs >= target:
                # Chasing team won
                innings.is_completed = True
                innings.save()
                innings_ended = True
                match_ended = True
                winner = innings.batting_team
                wickets_remaining = 10 - innings.total_wickets
                result_desc = f"{winner.team_name} won by {wickets_remaining} wickets."
                cls._conclude_match(match, winner, result_desc)

            elif max_overs_reached or all_out:
                # Defending team won or tied
                innings.is_completed = True
                innings.save()
                innings_ended = True
                match_ended = True

                if innings.total_runs == (target - 1):
                    result_desc = "Match Tied."
                    cls._conclude_match(match, None, result_desc, is_tie=True)
                else:
                    winner = innings.bowling_team
                    runs_margin = (target - 1) - innings.total_runs
                    result_desc = f"{winner.team_name} won by {runs_margin} runs."
                    cls._conclude_match(match, winner, result_desc)

        # 5. Broadcast live update to WebSockets group
        try:
            channel_layer = get_channel_layer()
            if channel_layer:
                broadcast_data = {
                    "type": "match_update",
                    "data": {
                        "match_id": match.id,
                        "innings_number": innings.innings_number,
                        "total_runs": innings.total_runs,
                        "total_wickets": innings.total_wickets,
                        "total_overs": str(innings.total_overs),
                        "recent_ball": {
                            "runs": runs_scored,
                            "extra_type": extra_type,
                            "is_wicket": is_wicket,
                            "commentary": commentary_text
                        },
                        "is_over_complete": is_over_complete,
                        "match_ended": match_ended,
                        "result_description": result_desc
                    }
                }
                async_to_sync(channel_layer.group_send)(
                    f"match_{match.id}",
                    broadcast_data
                )
        except Exception:
            pass  # Fallback gracefully if Redis is temporarily unreachable

        return {
            "ball_id": ball.id,
            "innings_total_runs": innings.total_runs,
            "innings_total_wickets": innings.total_wickets,
            "innings_total_overs": str(innings.total_overs),
            "next_striker_id": next_striker.id if next_striker else None,
            "next_non_striker_id": next_non_striker.id if next_non_striker else None,
            "is_over_complete": is_over_complete,
            "innings_ended": innings_ended,
            "match_ended": match_ended,
            "result_description": result_desc,
        }

    @classmethod
    @transaction.atomic
    def undo_last_delivery(cls, innings):
        """
        Reverts the last recorded ball delivery and recalculates innings state.
        """
        last_ball = innings.balls.last()
        if not last_ball:
            return None, "No deliveries to undo."

        # Delete the latest ball
        last_ball.delete()

        # Recalculate Innings total from remaining deliveries
        remaining_balls = innings.balls.all()
        legal_count = remaining_balls.filter(extra_type__in=['none', 'bye', 'leg_bye', 'penalty']).count()

        runs_data = remaining_balls.aggregate(
            r=Sum('runs_scored'),
            e=Sum('extra_runs'),
            w=Count('id', filter=Q(is_wicket=True) & ~Q(wicket_type='retired_hurt'))
        )

        innings.total_runs = (runs_data['r'] or 0) + (runs_data['e'] or 0)
        innings.total_wickets = runs_data['w'] or 0
        innings.total_overs = Decimal(f"{legal_count // 6}.{legal_count % 6}")
        innings.is_completed = False
        innings.save()

        # Revert match status if it was completed
        match = innings.match
        if match.status in ['completed', 'innings_break']:
            match.status = 'live'
            match.winner = None
            match.result_description = None
            match.save()

        return innings, "Last delivery undone successfully."

    @classmethod
    def _conclude_match(cls, match, winner, result_desc, is_tie=False):
        """
        Marks match as completed and updates points table & NRR automatically.
        """
        match.status = 'completed'
        match.winner = winner
        match.result_description = result_desc
        match.save()

        # Update tournament standings
        cls.recalculate_tournament_points(match.tournament)

    @staticmethod
    def recalculate_tournament_points(tournament):
        """
        Recomputes Points Table & Net Run Rate (NRR) for all teams in the tournament.
        """
        teams = CollegeRegistration.objects.filter(
            Q(home_matches__tournament=tournament) | Q(away_matches__tournament=tournament)
        ).distinct()

        for team in teams:
            pt, _ = PointsTable.objects.get_or_create(tournament=tournament, team=team)

            completed_matches = Match.objects.filter(
                Q(team_a=team) | Q(team_b=team),
                tournament=tournament,
                status='completed'
            )

            matches_played = completed_matches.count()
            won = completed_matches.filter(winner=team).count()
            lost = completed_matches.exclude(winner=team).exclude(winner__isnull=True).count()
            tied = completed_matches.filter(winner__isnull=True, result_description__icontains='Tied').count()
            no_result = completed_matches.filter(winner__isnull=True).exclude(result_description__icontains="Tied").count()

            points = (won * 2) + (tied * 1) + (no_result * 1)

            # --- NRR Calculation ---
            batting_innings = Innings.objects.filter(match__in=completed_matches, batting_team=team)
            total_runs_scored = 0
            total_overs_faced = Decimal('0.0')

            for inn in batting_innings:
                total_runs_scored += inn.total_runs
                if inn.total_wickets >= 10:
                    total_overs_faced += Decimal(str(inn.match.total_overs))
                else:
                    over_split = str(inn.total_overs).split('.')
                    ov = int(over_split[0])
                    bl = int(over_split[1]) if len(over_split) > 1 else 0
                    total_overs_faced += Decimal(str(ov + (bl / 6.0)))

            bowling_innings = Innings.objects.filter(match__in=completed_matches, bowling_team=team)
            total_runs_conceded = 0
            total_overs_bowled = Decimal('0.0')

            for inn in bowling_innings:
                total_runs_conceded += inn.total_runs
                if inn.total_wickets >= 10:
                    total_overs_bowled += Decimal(str(inn.match.total_overs))
                else:
                    overs_split = str(inn.total_overs).split('.')
                    ov = int(overs_split[0])
                    bl = int(overs_split[1]) if len(overs_split) > 1 else 0
                    total_overs_bowled += Decimal(str(ov + (bl / 6.0)))

            batting_run_rate = (total_runs_scored / total_overs_faced) if total_overs_faced > 0 else Decimal('0.0')
            bowling_run_rate = (total_runs_conceded / total_overs_bowled) if total_overs_bowled > 0 else Decimal('0.0')
            nrr = round(Decimal(str(batting_run_rate - bowling_run_rate)), 3)

            pt.matches_played = matches_played
            pt.won = won
            pt.lost = lost
            pt.tied = tied
            pt.no_result = no_result
            pt.points = points
            pt.net_run_rate = nrr
            pt.save()