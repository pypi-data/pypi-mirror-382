from datetime import datetime, timedelta
from os import stat
import click
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.align import Align
from rich.table import Table
from rich import box
import time
from grit_guardian_cli.guardian.guardian import Guardian, GuardianMood
from grit_guardian_cli.analytics.analytics import identify_struggled_habits

console = Console()


class GritUI:
    # Color scheme
    GOLD = "gold1"
    SILVER = "bright_white"
    BRONZE = "dark_orange"
    DRAGON_GREEN = "green"
    QUEST_BLUE = "bright_blue"
    WARNING_RED = "red"
    MYSTICAL_PURPLE = "magenta"

    # Unicode medieval symbols
    SWORD = "⚔️"
    SHIELD = "🛡️"
    CROWN = "👑"
    SCROLL = "📜"
    CASTLE = "🏰"
    DRAGON = "🐉"
    STAR = "⭐"
    FIRE = "🔥"
    CRYSTAL = "💎"
    POTION = "🧪"

    @staticmethod
    def show_banner():
        """Displays the main Grit Guardian banner"""
        banner_text = """
            ╔══════════════════════════════════════════════════════════╗
            ║                  🏰  GRIT GUARDIAN  🏰                   ║
            ║              ⚔️  Quest Management System  ⚔️             ║
            ║                                                          ║
            ║        "Forge your destiny, one habit at a time"         ║
            ╚══════════════════════════════════════════════════════════╝
        """

        console.print(banner_text, style=f"bold {GritUI.GOLD}")

    @staticmethod
    def show_help_menu():
        """Show available commands in medieval style"""
        help_text = Text()
        help_text.append(
            f"\n{GritUI.SCROLL} Available Commands:\n",
            style=f"bold {GritUI.GOLD}",
        )

        commands = [
            ("init", "🌟 Awaken your Guardian"),
            ("add", "⚔️ Accept a new quest"),
            ("list", "📜 View Quest Log"),
            ("status", "🏰 Today's status"),
            ("complete", "✅ Complete quest"),
            ("guardian", "🐉 Visit Guardian"),
            ("streaks", "🔥 Hall of Deeds"),
            ("weekly", "📅 Quest Chronicle"),
            ("struggled", "⚠️ Needs focus"),
        ]

        for cmd, desc in commands:
            help_text.append(f"  {desc:<25}", style=GritUI.SILVER)
            help_text.append(f"grit-guardian {cmd}\n", style=GritUI.QUEST_BLUE)

        console.print(help_text)

    @staticmethod
    def show_quest_added(habit_name, task, periodicity):
        """Shows success message for new quest (habit)."""
        message = Text()
        message.append(f"\n{GritUI.SCROLL} ", style=GritUI.GOLD)
        message.append("QUEST ACCEPTED", style=f"bold {GritUI.GOLD}")
        message.append(f" {GritUI.SCROLL}\n", style=GritUI.GOLD)
        message.append(
            f"'{habit_name}' has been inscribed in your Quest Log\n",
            style=GritUI.SILVER,
        )
        message.append(
            f"Quest: {task.capitalize()} ({periodicity.capitalize()})",
            style=GritUI.QUEST_BLUE,
        )
        console.print(
            Panel(message, border_style=GritUI.DRAGON_GREEN, title="⚔️ New Quest")
        )

    @staticmethod
    def show_error(error_message):
        """Displays in theme error messages."""
        error_panel = Panel(
            f"⚠️  {error_message}",
            title="🔥 Dark Magic Interference",
            border_style=GritUI.WARNING_RED,
        )
        console.print(error_panel)

    @staticmethod
    def show_loading():
        with click.progressbar(range(10), label="Initializing...") as bar:
            for i in bar:
                time.sleep(0.1)

    @staticmethod
    def show_quest_log(habits):
        """Display all quests in theme."""
        if not habits:
            GritUI.show_no_quests_message()
            return

        table = Table(title=f"{GritUI.SCROLL} Active Quests", box=box.ROUNDED)
        table.add_column("Quest Name", style=GritUI.GOLD, width=20)
        table.add_column("Objective", style=GritUI.SILVER, width=30)
        table.add_column("Frequency", style=GritUI.QUEST_BLUE, width=10)
        table.add_column("Status", style=GritUI.DRAGON_GREEN, width=10)

        for habit in habits:
            status = f"{GritUI.SHIELD} Active"
            table.add_row(
                f"{GritUI.SWORD} {habit.name}",
                habit.task,
                habit.periodicity.value.title(),
                status,
            )

        console.print(table)

    @staticmethod
    def show_no_quests_message():
        """Show message when no quests are available"""
        console.print(
            Panel(
                Text(
                    "Your Quest Log is empty, brave adventurer!\n"
                    "Use 'grit-guardian add' to accept new quests from the Guild Hall.",
                    style=GritUI.SILVER,
                    justify="center",
                ),
                title=f"{GritUI.SCROLL} Empty Quest Log",
                border_style=GritUI.BRONZE,
            )
        )

    @staticmethod
    def confirm_quest_abandonment(quest_name):
        """In-theme confirmation for quest deletion."""
        console.print(
            f"\n{GritUI.SCROLL} [bold {GritUI.WARNING_RED}]Quest Abandonment Warning[/]"
        )
        console.print(
            f"Are you certain you wish to abandon the quest '{quest_name}'?",
            style=GritUI.SILVER,
        )
        console.print("This action cannot be undone...", style=GritUI.BRONZE)

        return click.confirm("Proceed with abandonment?")

    @staticmethod
    def show_quest_abandoned(quest_name):
        """Show quest abandonment message"""
        message = (
            f"{GritUI.SCROLL} Quest '{quest_name}' has been removed from your log."
        )
        console.print(
            Panel(message, border_style=GritUI.BRONZE, title="Quest Abandoned")
        )

    @staticmethod
    def show_quest_completed(habit_name):
        """Shows success message for completed quest."""
        message = Text()
        message.append(
            f"{GritUI.STAR} QUEST COMPLETED! {GritUI.STAR}\n",
            style=f"bold {GritUI.GOLD}",
        )
        message.append(
            f"You have successfully completed: '{habit_name}'\n",
            style=GritUI.SILVER,
        )
        message.append(
            f"{GritUI.CRYSTAL} Experience gained! Your Guardian grows stronger!",
            style=GritUI.MYSTICAL_PURPLE,
        )

        console.print(Panel(message, border_style=GritUI.GOLD))

    @staticmethod
    def show_guardian_status(guardian):
        """Display Guardian."""
        console.print(
            f"\n{GritUI.DRAGON} [bold {GritUI.MYSTICAL_PURPLE}]Your Mystical Guardian[/]"
        )
        console.print("═" * 50, style=GritUI.MYSTICAL_PURPLE)

        # Show ASCII art in a panel
        art_panel = Panel(
            guardian.get_ascii_art(),
            title=f"{GritUI.CRYSTAL} {guardian.name}",
            border_style=GritUI.DRAGON_GREEN,
        )
        console.print(art_panel)

        # Show mood and message
        mood_colors = {
            "ecstatic": GritUI.GOLD,
            "happy": GritUI.DRAGON_GREEN,
            "content": GritUI.QUEST_BLUE,
            "worried": GritUI.BRONZE,
            "sad": GritUI.WARNING_RED,
        }

        mood_color = mood_colors.get(guardian.current_mood.value, GritUI.SILVER)
        console.print(f"\n{GritUI.CROWN} Guardian's Spirit: ", end="")
        console.print(
            guardian.current_mood.value.capitalize(), style=f"bold {mood_color}"
        )

        message_panel = Panel(
            guardian.get_mood_message(),
            title="Guardian's Wisdom",
            border_style=mood_color,
        )
        console.print(message_panel)

    @staticmethod
    def show_guardian_reaction(guardian):
        """Shows quick guardian reaction after quest completion."""
        reactions = {
            GuardianMood.ECSTATIC: f"{GritUI.CROWN} Your Guardian radiates pure joy!",
            GuardianMood.HAPPY: f"{GritUI.STAR} Your Guardian beams with pride!",
            GuardianMood.CONTENT: f"{GritUI.CRYSTAL} Your Guardian nods approvingly.",
            GuardianMood.WORRIED: f"{GritUI.POTION} Your Guardian looks hopeful...",
            GuardianMood.SAD: f"{GritUI.FIRE} Your Guardian's spirits lift slightly.",
        }

        reaction = reactions.get(
            guardian.current_mood.value, "Your Guardian acknowledges your effort."
        )
        console.print(f"\n{reaction}", style=GritUI.MYSTICAL_PURPLE)

    @staticmethod
    def show_daily_status(status):
        """Shows today's quest status in medieval style."""
        console.print(f"\n{GritUI.CASTLE} [bold {GritUI.GOLD}]Today's Quest Status[/]")
        console.print("═" * 50, style=GritUI.GOLD)

        if status["pending"]:
            console.print(f"\n{GritUI.SCROLL} [bold {GritUI.BRONZE}]Pending Quests:[/]")
            for habit in status["pending"]:
                console.print(f"  ⏳ {habit.name}", style=GritUI.SILVER)

        if status["completed"]:
            console.print(
                f"\n{GritUI.CRYSTAL} [bold {GritUI.DRAGON_GREEN}]Completed Quests:[/]"
            )
            for habit in status["completed"]:
                console.print(f"  ✅ {habit.name}", style=GritUI.DRAGON_GREEN)

        if not status["pending"] and not status["completed"]:
            GritUI.show_no_quests_message()
        else:
            progress = f"{len(status['completed'])}/{status['total']}"
            console.print(
                f"\n{GritUI.SHIELD} Quest Progress: {progress}",
                style=f"bold {GritUI.QUEST_BLUE}",
            )
            if len(status["completed"]) == status["total"] and status["total"] > 0:
                console.print(
                    f"\n{GritUI.CROWN} [bold {GritUI.GOLD}]ALL QUESTS COMPLETED![/]"
                )
                console.print(
                    "🎉 Your Guardian beams with pride! The realm prospers!",
                    style=GritUI.MYSTICAL_PURPLE,
                )

    @staticmethod
    def show_streaks(streaks_data, total_streaks, avg_completion_rate):
        """Display streaks as heroic achievements."""

        if not streaks_data:
            console.print("No heroic deeds to display yet!", style=GritUI.BRONZE)
            return

        console.print("\n🔥 Hall of Heroic Deeds")
        console.print("=" * 60)

        console.print("\n Achievement Records")
        for streak_info in streaks_data:
            console.print(f"\n {streak_info['name']}")
            console.print(f"   Current Streak: {streak_info['current_streak']} days")
            console.print(f"   Longest Streak: {streak_info['longest_streak']} days")
            console.print(f"   Completion Rate: {streak_info['completion_rate']:.1f}%")

        console.print("\n" + "-" * 60)
        console.print("Overall Stats:")
        console.print(f"   Total Active Streaks: {total_streaks}")
        console.print(f"   Average Success Rate: {avg_completion_rate:.1f}%")

        # Alternative with achievement badges for later versions
        """
        console.print(
            f"\n{GritUI.FIRE} [bold {GritUI.GOLD}]Hall of Heroic Deeds[/]"
        )
        console.print("═" * 60, style=GritUI.GOLD)

        table = Table(box=box.ROUNDED, title=f"{GritUI.SHIELD} Achievement Records")
        table.add_column("Quest", style=GritUI.GOLD)
        table.add_column("Current Streak", style=GritUI.FIRE)
        table.add_column("Longest Streak", style=GritUI.CRYSTAL)
        table.add_column("Success Rate", style=GritUI.DRAGON_GREEN)
        for streak_info in streaks_data:
            # Add achievement badges based on streaks
            badge = ""
            if streak_info["current_streak"] >= 30:
                badge = f"{GritUI.CROWN} "
            elif streak_info["current_streak"] >= 7:
                badge = f"{GritUI.CRYSTAL} "
            elif streak_info["current_streak"] >= 3:
                badge = f"{GritUI.STAR} "

            table.add_row(
                f"{badge}{streak_info['name']}",
                f"{streak_info['current_streak']} days",
                f"{streak_info['longest_streak']} days",
                f"{streak_info['completion_rate']:.1f}%",
            )

        console.print(table)
        """

    @staticmethod
    def create_weekly_table(habits):
        """Creates a Rich table showing weekly progress for all habits."""

        # Create the table
        table = Table(
            title=f"{GritUI.SCROLL} Weekly Quest Chronicle",
            box=box.HEAVY_EDGE,
            title_style=GritUI.MYSTICAL_PURPLE,
            header_style=GritUI.QUEST_BLUE,
        )

        # Add columns with day names and dates
        today = datetime.now().date()
        week_start = today - timedelta(days=today.weekday())

        table.add_column("Quest", style=f"bold {GritUI.GOLD}", width=18)

        day_names = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

        for i, day_name in enumerate(day_names):
            day_date = week_start + timedelta(days=i)
            column_title = f"{day_name}\n{day_date.day}"
            table.add_column(column_title, justify="center", width=6)

        # Process each habit
        for habit in habits:
            row = [f"{GritUI.SWORD} {habit.name[:15]}"]  # Truncate long names

            for i in range(7):
                day_date = week_start + timedelta(days=i)
                symbol = GritUI._get_symbol_for_date(habit, day_date, today)
                row.append(symbol)

            table.add_row(*row)

        return table

    @staticmethod
    def _get_symbol_for_date(habit, date, today):
        """Gets completion symbol for a specific date."""
        if date > today:
            return "[dim]-[/dim]"

        if hasattr(habit, "completions"):
            if date in habit.completions:
                return "[bold green]✓[/bold green]"
            else:
                return "[bold red]✗[/bold red]"

        return "[yellow]?[/yellow]"

    @staticmethod
    def show_weekly_progress(habits):
        """Display weekly progress in theme."""

        # Show current week info
        today = datetime.now()
        week_start = today - timedelta(days=today.weekday())
        week_end = week_start + timedelta(days=6)

        console.print(
            f"\n🗓️  Week of {week_start.strftime('%B %d')} - {week_end.strftime('%B %d, %Y')}"
        )

        table = GritUI.create_weekly_table(habits)
        console.print(table)

        # Show legend
        legend = Text()
        legend.append("\n📖 Legend: ", style="bold GritUI.GOLD")
        legend.append("✓ = Victory achieved", style="bold green")
        legend.append("  |  ", style="white")
        legend.append("✗ = Defeat", style="bold red")
        legend.append("  |  ", style="white")
        legend.append("- = Future Battles", style="dim white")

        console.print(legend)

        # Show weekly stats
        GritUI._show_weekly_stats(habits)

    @staticmethod
    def _show_weekly_stats(habits):
        """Show weekly completion statistics."""
        if not habits:
            return

        today = datetime.now().date()
        days_since_monday = today.weekday()
        monday = today - timedelta(days=days_since_monday)

        total_possible = 0
        total_completed = 0

        for habit in habits:
            for i in range(days_since_monday + 1):  # Only count days up to today
                day_date = monday + timedelta(days=i)
                total_possible += 1

                # Check if completed
                if hasattr(habit, "completed_at") and habit.completed_at(day_date):
                    total_completed += 1
                elif hasattr(habit, "completions"):
                    completion_dates = [comp.date for comp in habit.completions]
                    if day_date in completion_dates:
                        total_completed += 1

        if total_possible > 0:
            completion_rate = (total_completed / total_possible) * 100
            console.print(
                f"\n📊 Week Progress: {total_completed}/{total_possible} quests completed ({completion_rate:.1f}%)"
            )

            # Motivational message based on performance
            if completion_rate >= 90:
                console.print("🏆 Legendary performance!", style=f"bold {GritUI.GOLD}")
            elif completion_rate >= 75:
                console.print(
                    "⭐ Excellent dedication!", style=f"bold {GritUI.DRAGON_GREEN}"
                )
            elif completion_rate >= 50:
                console.print("🗡️ Steady progress!", style=f"bold {GritUI.QUEST_BLUE}")
            else:
                console.print(
                    "💪 Room for improvement - you've got this!",
                    style=f"bold {GritUI.BRONZE}",
                )

    @staticmethod
    def show_struggled_habits(struggled_habits, since):
        if not struggled_habits:
            console.print(
                f"\n🌟 Great job! No struggled habits in the last {since} days."
            )
            console.print("Keep up the excellent work!")
        else:
            console.print(f"\n⚠️  Habits needing attention (last {since} days):")
            console.print("=" * 50)

            for habit in struggled_habits:
                percentage = habit["completion_rate"] * 100
                console.print(f"\n• {habit['name']}")
                console.print(f"  Completion rate: {percentage:.0f}%")
                console.print(f"  Missed: {habit['missed']} times")

            console.print("\n💡 Tip: Focus on one habit at a time to build momentum!")

    @staticmethod
    def show_struggled_habits_alternative(struggled_habits, days):
        """Show struggled habits as fallen quests."""
        if not struggled_habits:
            success_message = Text()
            success_message.append(f"{GritUI.CROWN} ", style=GritUI.GOLD)
            success_message.append("FLAWLESS VICTORY!", style=f"bold {GritUI.GOLD}")
            success_message.append(
                f"\nNo fallen quests in the last {days} days.\n",
                style=GritUI.DRAGON_GREEN,
            )
            success_message.append(
                "Your Guardian radiates with pride!", style=GritUI.MYSTICAL_PURPLE
            )

            console.print(Panel(success_message, border_style=GritUI.GOLD))
        else:
            console.print(
                f"\n⚔️ [bold {GritUI.WARNING_RED}]Quests Requiring Renewed Focus[/] (last {days} days)"
            )
            console.print("═" * 55, style=GritUI.WARNING_RED)

            for habit in struggled_habits:
                percentage = habit["completion_rate"] * 100
                console.print(
                    f"\n{GritUI.SCROLL} {habit['name']}",
                    style=f"bold {GritUI.BRONZE}",
                )
                console.print(f"  Victory Rate: {percentage:.0f}%", style=GritUI.SILVER)
                console.print(
                    f"  Defeats: {habit['missed']} times", style=GritUI.WARNING_RED
                )

            tip_message = Text()
            tip_message.append(
                f"\n{GritUI.CRYSTAL} Guardian's Wisdom: ",
                style=GritUI.MYSTICAL_PURPLE,
            )
            tip_message.append(
                "Focus your strength on one quest at a time!",
                style=GritUI.QUEST_BLUE,
            )
            console.print(tip_message)

    @staticmethod
    def show_initialization():
        """Shows dramatic initialization sequence."""
        console.clear()
        GritUI.show_banner()

        # Dramatic pause with loading effect
        with console.status("[bold magenta]Awakening your Guardian...") as status:
            time.sleep(1)
            status.update("[bold blue]Forging your destiny...")
            time.sleep(1)
            status.update("[bold green]Preparing your quest log...")
            time.sleep(1)

        success_message = Text()
        success_message.append(f"\n{GritUI.DRAGON} ", style=GritUI.MYSTICAL_PURPLE)
        success_message.append("GUARDIAN AWAKENED", style=f"bold {GritUI.GOLD}")
        success_message.append(f" {GritUI.DRAGON}\n", style=GritUI.MYSTICAL_PURPLE)
        success_message.append(
            "Your companion is ready to guide your journey!\n",
            style=GritUI.SILVER,
        )
        success_message.append(
            "Sample quests have been prepared for your consideration.\n",
            style=GritUI.QUEST_BLUE,
        )
        success_message.append(
            f"{GritUI.SCROLL} Begin with 'grit-guardian status' to see your current quests",
            style=GritUI.BRONZE,
        )

        console.print(Panel(success_message, border_style=GritUI.GOLD))

    @staticmethod
    def show_initialization_simple():
        console.print("\n🐉 Welcome to Grit Guardian!\n")
        GritUI.show_loading()
        console.print("\nYour Quest Begins Now\n")

    @staticmethod
    def show_get_started():
        console.print("\n🎯 Quick Start Guide:")
        console.print("  - View your quests (habits): grit-guardian list")
        console.print("  - Complete a quest: grit-guardian complete 'Morning Reading'")
        console.print("  - Check your Guardian: grit-guardian guardian")
        console.print("  - See weekly progress: grit-guardian weekly")
        console.print("  - View your streaks: grit-guardian streaks")
        console.print("\nYour Guardian is waiting to see your progress!")

    @staticmethod
    def show_guardian(guardian):
        console.print("Your Guardian")
        console.print(guardian.get_ascii_art())
        console.print(f"Name: {guardian.name}")
        console.print(f"Species: {guardian.species}")

    @staticmethod
    def show_already_initialized():
        console.print("Grit Guardian is already initialized.")
        console.print("Use 'grit-guardian status' to see today's quests.")

    @staticmethod
    def show_sample_quests(habits):
        console.print("✓ Created beginner quests to get you started:")
        for habit in habits:
            console.print(f"  • {habit.name} - {habit.task}")


"""
  .,-:::::/ :::::::..   :::::::::::::::      .,-:::::/   ...    :::  :::.    :::::::.. :::::::-.  :::  :::.   :::.    :::.
,;;-'````'  ;;;;``;;;;  ;;;;;;;;;;;''''    ,;;-'````'    ;;     ;;;  ;;`;;   ;;;;``;;;; ;;,   `';,;;;  ;;`;;  `;;;;,  `;;;
[[[   [[[[[[/[[[,/[[['  [[[     [[         [[[   [[[[[[/[['     [[[ ,[[ '[[,  [[[,/[[[' `[[     [[[[[ ,[[ '[[,  [[[[[. '[[
"$$c.    "$$ $$$$$$c    $$$     $$         "$$c.    "$$ $$      $$$c$$$cc$$$c $$$$$$c    $$,    $$$$$c$$$cc$$$c $$$ "Y$c$$
 `Y8bo,,,o88o888b "88bo,888     88,         `Y8bo,,,o88o88    .d888 888   888,888b "88bo,888_,o8P'888 888   888,888    Y88
   `'YMUP"YMMMMMM   "W" MMM     MMM           `'YMUP"YMM "YmmMMMM"" YMM   ""` MMMM   "W" MMMMP"`  MMM YMM   ""` MMM     YM
"""


"""
   █████████             ███   █████         █████████                                     █████  ███                      
  ███░░░░░███           ░░░   ░░███         ███░░░░░███                                   ░░███  ░░░                       
 ███     ░░░  ████████  ████  ███████      ███     ░░░  █████ ████  ██████   ████████   ███████  ████   ██████   ████████  
░███         ░░███░░███░░███ ░░░███░      ░███         ░░███ ░███  ░░░░░███ ░░███░░███ ███░░███ ░░███  ░░░░░███ ░░███░░███ 
░███    █████ ░███ ░░░  ░███   ░███       ░███    █████ ░███ ░███   ███████  ░███ ░░░ ░███ ░███  ░███   ███████  ░███ ░███ 
░░███  ░░███  ░███      ░███   ░███ ███   ░░███  ░░███  ░███ ░███  ███░░███  ░███     ░███ ░███  ░███  ███░░███  ░███ ░███ 
 ░░█████████  █████     █████  ░░█████     ░░█████████  ░░████████░░████████ █████    ░░████████ █████░░████████ ████ █████
  ░░░░░░░░░  ░░░░░     ░░░░░    ░░░░░       ░░░░░░░░░    ░░░░░░░░  ░░░░░░░░ ░░░░░      ░░░░░░░░ ░░░░░  ░░░░░░░░ ░░░░ ░░░░░ 
                                                                                                                           
                                                                                                                           
"""


"""
      ....        .                   .         s             ....        .                                              ..          .                              
   .x88" `^x~  xH(`                  @88>      :8          .x88" `^x~  xH(`                                            dF           @88>                            
  X888   x8 ` 8888h      .u    .     %8P      .88         X888   x8 ` 8888h      x.    .                    .u    .   '88bu.        %8P                  u.    u.   
 88888  888.  %8888    .d88B :@8c     .      :888ooo     88888  888.  %8888    .@88k  z88u         u      .d88B :@8c  '*88888bu      .          u      x@88k u@88c. 
<8888X X8888   X8?    ="8888f8888r  .@88u  -*8888888    <8888X X8888   X8?    ~"8888 ^8888      us888u.  ="8888f8888r   ^"*8888N   .@88u     us888u.  ^"8888""8888" 
X8888> 488888>"8888x    4888>'88"  ''888E`   8888       X8888> 488888>"8888x    8888  888R   .@88 "8888"   4888>'88"   beWE "888L ''888E` .@88 "8888"   8888  888R  
X8888>  888888 '8888L   4888> '      888E    8888       X8888>  888888 '8888L   8888  888R   9888  9888    4888> '     888E  888E   888E  9888  9888    8888  888R  
?8888X   ?8888>'8888X   4888>        888E    8888       ?8888X   ?8888>'8888X   8888  888R   9888  9888    4888>       888E  888E   888E  9888  9888    8888  888R  
 8888X h  8888 '8888~  .d888L .+     888E   .8888Lu=     8888X h  8888 '8888~   8888 ,888B . 9888  9888   .d888L .+    888E  888F   888E  9888  9888    8888  888R  
  ?888  -:8*"  <888"   ^"8888*"      888&   ^%888*        ?888  -:8*"  <888"   "8888Y 8888"  9888  9888   ^"8888*"    .888N..888    888&  9888  9888   "*88*" 8888" 
   `*88.      :88%        "Y"        R888"    'Y"          `*88.      :88%      `Y"   'YP    "888*""888"     "Y"       `"888*""     R888" "888*""888"    ""   'Y"   
      ^"~====""`                      ""                      ^"~====""`                      ^Y"   ^Y'                   ""         ""    ^Y"   ^Y'                
                                                                                                                                                                    
                                                                                                                                                                    
"""
