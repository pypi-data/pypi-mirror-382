"""CLI tool for transforming GNPS systems to various output formats."""

import argparse
import sys
from pathlib import Path
from typing import Dict, Type

from gnps.system import GnpsSystem
from gnps.transformers import BaseTransformer, PythonTransformer
from gnps._version import __version__


# Registry of available transformers
TRANSFORMERS: Dict[str, Type[BaseTransformer]] = {
    'python': PythonTransformer,
}


def get_transformer(transform_type: str) -> BaseTransformer:
    """Get a transformer instance by type name.

    Args:
        transform_type: The type of transformer to create

    Returns:
        Transformer instance

    Raises:
        ValueError: If transform_type is not supported
    """
    if transform_type not in TRANSFORMERS:
        available = ', '.join(TRANSFORMERS.keys())
        raise ValueError(f"Unsupported transformation type '{transform_type}'. Available types: {available}")

    return TRANSFORMERS[transform_type]()


def main():
    """Main entry point for the gnps-transformer CLI."""
    parser = argparse.ArgumentParser(
        description=f"GNPS Transformer v{__version__} - Convert GNPS systems to various output formats",
        prog='gnps-transformer'
    )

    parser.add_argument(
        'gnps_files',
        nargs='+',
        help='GNPS system files (.yaml) to transform'
    )

    parser.add_argument(
        '-t', '--type',
        dest='transform_type',
        required=True,
        choices=list(TRANSFORMERS.keys()),
        help='Transformation type'
    )

    parser.add_argument(
        '-o', '--output-dir',
        type=Path,
        default=Path('.'),
        help='Output directory for transformed files (default: current directory)'
    )

    parser.add_argument(
        '--output-suffix',
        default='',
        help='Suffix to add to output filenames (before extension)'
    )

    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Enable verbose output'
    )

    args = parser.parse_args()

    # Ensure output directory exists
    args.output_dir.mkdir(parents=True, exist_ok=True)

    # Get transformer
    try:
        transformer = get_transformer(args.transform_type)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    # Process each file
    for gnps_file_path in args.gnps_files:
        gnps_file = Path(gnps_file_path)

        if not gnps_file.exists():
            print(f"Error: File '{gnps_file}' not found", file=sys.stderr)
            continue

        if args.verbose:
            print(f"Processing: {gnps_file}")

        try:
            # Load GNPS system
            gnps_system = GnpsSystem.from_yaml(str(gnps_file))

            # Transform to target format
            transformed_code = transformer.transform(gnps_system)

            # Generate output filename
            base_name = gnps_file.stem
            if args.output_suffix:
                base_name += args.output_suffix

            output_file = args.output_dir / (base_name + transformer.get_file_extension())

            # Write output
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(transformed_code)

            if args.verbose:
                print(f"  -> {output_file}")

        except Exception as e:
            print(f"Error processing '{gnps_file}': {e}", file=sys.stderr)
            if args.verbose:   # pragma: no cover
                import traceback
                traceback.print_exc()
            continue

    if args.verbose:
        print("Transformation complete.")


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(f"Error: {e}")