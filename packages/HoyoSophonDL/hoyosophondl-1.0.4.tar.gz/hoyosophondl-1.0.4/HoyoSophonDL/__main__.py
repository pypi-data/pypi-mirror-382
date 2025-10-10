import argparse
import sys
from rich.console import Console
from rich.progress import (
    Progress,
    BarColumn,
    TextColumn,
    TimeElapsedColumn,
    TimeRemainingColumn,
    DownloadColumn,
    TaskProgressColumn,
)
from HoyoSophonDL import HoyoSophonDL, Branch, Region
from HoyoSophonDL.download import GlobalDownloadData


console = Console()


def rich_download(launcher: HoyoSophonDL, assets, output_dir, workers):
    download_info = launcher.set_download_assets(assets, output_dir, workers)
    trace: GlobalDownloadData = launcher.trace_download
    with Progress(
        TextColumn("[cyan]{task.description}"),
        BarColumn(),
        TaskProgressColumn(),
        DownloadColumn(),
        TimeRemainingColumn(),
        TimeElapsedColumn(),
        console=console,
        transient=False,
        refresh_per_second=5,
    ) as progress:

        main_task = progress.add_task(
            f"Downloading {assets.GameData.Name}", total=trace.TotalSize
        )

        def on_progress(_trace: GlobalDownloadData):
            # Update main task progress
            progress.update(
                main_task,
                completed=_trace.TotalDownloadBytes,
                description=(
                    f"[cyan]{assets.GameData.Name}[/cyan] "
                    f"[{_trace.CompletedAssets}/{_trace.TotalAssetsCount} assets] "
                    f"[{_trace.CompletedChunks}/{_trace.TotalChunksCount} chunks] "
                    f"{_trace.Percent}"
                ),
            )

        def on_finish(_trace: GlobalDownloadData):
            progress.update(main_task, completed=_trace.TotalSize)
            console.print(
                f"[green]Download completed for {assets.GameData.Name}![/green]"
            )

        def on_cancel(_trace: GlobalDownloadData):
            console.print(f"[yellow]Download cancelled at {_trace.Percent}[/yellow]")

        def on_pause(_trace: GlobalDownloadData):
            console.print(f"[blue]Paused... {_trace.Percent}[/blue]")

        # Run download
        launcher.download_assets(download_info,on_progress, on_finish, on_cancel, on_pause)


def main():
    parser = argparse.ArgumentParser(
        prog="HoyoSophonDL",
        description="HoyoSophonDL CLI is a Python-based reimplementation of HoYoPlay’s downloader logic."
        "It allows users to list, validate, and download game assets directly from HoYoPlay manifests,"
        "with support for multi-threading, resumable downloads, and optional GUI mode.",
        formatter_class=argparse.RawTextHelpFormatter,
    )

    parser.add_argument("game", nargs="?", help="Game name")
    parser.add_argument(
        "-l", "--list", action="store_true", help="List available games"
    )
    parser.add_argument("-i", "--info", action="store_true", help="Show game info")
    parser.add_argument(
        "-ai", "--asset-info", action="store_true", help="Show asset info"
    )
    parser.add_argument("-d", "--download", action="store_true", help="Download assets")
    parser.add_argument(
        "-c", "--category", default="game", help="Asset category (default: 'game')"
    )
    parser.add_argument("-V", "--current", help="Current version")
    parser.add_argument("-U", "--update", help="Target update version")
    parser.add_argument("-o", "--output", default=".", help="Download output dir")
    parser.add_argument("-b", "--branch", default=Branch.MAIN, help="Launcher branch")
    parser.add_argument("-r", "--region", default=Region.EUROPE, help="Game region")
    parser.add_argument("--launcher-id", help="Override launcher ID")
    parser.add_argument("--launcher-platform", help="Override launcher platform ID")
    parser.add_argument(
        "-t", "--threads", type=int, default=20, help="Download threads"
    )
    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose logging")
    parser.add_argument("-g", "--gui", action="store_true", help="Start GUI")

    args = parser.parse_args()

    if args.gui:
        try:
            from HoyoSophonDL.gui import run_gui_pyqt6
        except ImportError:
            sys.exit("[ERROR] PyQt6 not installed or not supported on this system.")
        return run_gui_pyqt6()

    if args.game is None and not args.list:
        sys.exit("[ERROR] Provide a game name or use -l to list games")

    try:
        args.branch = Branch(args.branch)
        args.region = Region(args.region)
    except ValueError as e:
        sys.exit(f"[ERROR] {e}")

    launcher = HoyoSophonDL(
        branch=args.branch, region=args.region, verbose=args.verbose
    )

    if args.list:
        games = launcher.get_available_games()
        console.print("[bold cyan]Available games:[/bold cyan]")
        for g in games.Games:
            console.print(f" - {g.Name} (ID: {g.ID}, Lang: {g.Language})")
        return

    game = launcher.get_game_by_source(args.game)
    if not game:
        console.print(f"[red]Game '{args.game}' not found![/red]")
        return

    if args.info:
        info = launcher.get_game_info(game)
        console.print(f"[bold]{game.Name}[/bold] Latest: {info.LastVersion}")
        console.print(f"Other Versions: {info.OtherVersion}")
        console.print(f"Categories: {info.getCategoryByName()}")

    assets = None
    if args.asset_info:
        assets = launcher.get_assets_info(
            game, args.current, args.update, args.category
        )
        console.print(f"[bold]Assets for {game.Name}[/bold]")
        for k, v in assets.getDict().items():
            if k != "Assets":
                console.print(f"  {k}: {v}")

    if args.download:
        if assets is None:
            assets = launcher.get_assets_info(
                game, args.current, args.update, args.category
            )
        console.print(f"[green]Starting download for {game.Name}...[/green]")
        rich_download(launcher, assets, args.output, args.threads)


if __name__ == "__main__":
    main()
