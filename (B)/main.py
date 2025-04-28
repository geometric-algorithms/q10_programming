import argparse
from polygonal_area_drawer import PolygonalAreaDrawer

def main():
    """
    The main entry point of the application.

    This function sets up the graphical environment, initializes the main drawing Tkinter interface for the
    polygonal area, and starts the main event loop.
    """

    parser = argparse.ArgumentParser(description="Draw polygonal areas with triangulation.")
    parser.add_argument("use_tkinter", choices=["yes", "no"], help="Use Tkinter if 'yes', PIL if 'no'")
    parser.add_argument("--file", help="Input file with polygon vertices (required for PIL mode)")
    args = parser.parse_args()

    use_tkinter = args.use_tkinter.lower() == "yes"
    if not use_tkinter and not args.file:
        parser.error("The --file argument is required when use_tkinter is 'no'")
    drawer = PolygonalAreaDrawer(use_tkinter=use_tkinter, output_path="output.png")
    drawer.run(input_file=args.file)

if __name__ == "__main__":
    main()