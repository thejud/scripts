#!/usr/bin/env python3
"""
Convert MOV screen recordings to optimized GIFs for documentation.

This script converts MOV files to GIF format with options for:
- Resizing (default: 75% of original)
- Speed adjustment (default: 2x speed)
- Frame rate optimization
- Color palette optimization for smaller file sizes

Requirements:
    - ffmpeg (install with: brew install ffmpeg)
    - gifsicle (install with: brew install gifsicle)
"""

import argparse
import os
import subprocess
import sys
from pathlib import Path


def check_dependencies():
    """Check if required tools are installed."""
    dependencies = {
        'ffmpeg': (['ffmpeg', '-version'], 'brew install ffmpeg'),
        'gifsicle': (['gifsicle', '--version'], 'brew install gifsicle')
    }
    
    missing = []
    for tool, (check_cmd, install_cmd) in dependencies.items():
        try:
            subprocess.run(check_cmd, capture_output=True, check=True)
        except (subprocess.CalledProcessError, FileNotFoundError) as e:
            missing.append(f"{tool} (install with: {install_cmd})")
    
    if missing:
        print("Error: Missing required dependencies:")
        for dep in missing:
            print(f"  - {dep}")
        sys.exit(1)


def get_video_dimensions(input_file):
    """Get video dimensions using ffprobe."""
    cmd = [
        'ffprobe', '-v', 'error',
        '-select_streams', 'v:0',
        '-show_entries', 'stream=width,height',
        '-of', 'csv=s=x:p=0',
        str(input_file)
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True, check=True)
    width, height = map(int, result.stdout.strip().split('x'))
    return width, height


def mov_to_gif(input_file, output_file=None, scale=75, speed=2.0, fps=10, optimize=True):
    """
    Convert MOV to GIF with specified parameters.
    
    Args:
        input_file: Path to input MOV file
        output_file: Path to output GIF file (default: input_file.gif)
        scale: Scale percentage (default: 75)
        speed: Speed multiplier (default: 2.0 for 2x speed)
        fps: Output frame rate (default: 10)
        optimize: Whether to optimize the GIF (default: True)
    """
    input_path = Path(input_file)
    if not input_path.exists():
        print(f"Error: Input file '{input_file}' not found")
        sys.exit(1)
    
    if output_file is None:
        output_file = input_path.with_suffix('.gif')
    
    output_path = Path(output_file)
    
    # Get original dimensions
    orig_width, orig_height = get_video_dimensions(input_path)
    new_width = int(orig_width * scale / 100)
    new_height = int(orig_height * scale / 100)
    
    print(f"Converting: {input_path.name}")
    print(f"  Original size: {orig_width}x{orig_height}")
    print(f"  New size: {new_width}x{new_height} ({scale}%)")
    print(f"  Speed: {speed}x")
    print(f"  FPS: {fps}")
    
    # Create a temporary palette for better color optimization
    palette_file = output_path.with_suffix('.png')
    
    try:
        # Step 1: Generate optimized color palette
        print("Generating color palette...")
        palette_cmd = [
            'ffmpeg', '-y', '-i', str(input_path),
            '-vf', f'fps={fps},scale={new_width}:{new_height}:flags=lanczos,palettegen=stats_mode=diff',
            str(palette_file)
        ]
        subprocess.run(palette_cmd, check=True, capture_output=True)
        
        # Step 2: Create GIF using the palette
        print("Creating GIF...")
        gif_filters = [
            f'setpts={1/speed}*PTS',  # Adjust speed
            f'fps={fps}',              # Set frame rate
            f'scale={new_width}:{new_height}:flags=lanczos',  # Resize
            f'paletteuse=dither=bayer:bayer_scale=5:diff_mode=rectangle'  # Use palette
        ]
        
        gif_cmd = [
            'ffmpeg', '-y',
            '-i', str(input_path),
            '-i', str(palette_file),
            '-lavfi', ','.join(gif_filters),
            str(output_path)
        ]
        subprocess.run(gif_cmd, check=True, capture_output=True)
        
        # Step 3: Optimize with gifsicle if requested
        if optimize:
            print("Optimizing GIF...")
            optimize_cmd = [
                'gifsicle', '--optimize=3',
                '--colors=256',
                '--lossy=30',
                '-o', str(output_path),
                str(output_path)
            ]
            subprocess.run(optimize_cmd, check=True, capture_output=True)
        
        # Clean up palette file
        palette_file.unlink(missing_ok=True)
        
        # Get final file size
        file_size = output_path.stat().st_size / (1024 * 1024)  # MB
        print(f"\nSuccess! Created: {output_path}")
        print(f"File size: {file_size:.1f} MB")
        
    except subprocess.CalledProcessError as e:
        print(f"Error during conversion: {e}")
        # Clean up palette file on error
        palette_file.unlink(missing_ok=True)
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description='Convert MOV screen recordings to optimized GIFs',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Convert with defaults (75% size, 2x speed)
  %(prog)s recording.mov
  
  # Convert at 50%% size with 3x speed
  %(prog)s recording.mov -s 50 -x 3
  
  # Convert with custom output name and no optimization
  %(prog)s recording.mov -o demo.gif --no-optimize
  
  # High quality version (100%% size, normal speed, 15 fps)
  %(prog)s recording.mov -s 100 -x 1 -f 15
"""
    )
    
    parser.add_argument('input', help='Input MOV file')
    parser.add_argument('-o', '--output', help='Output GIF file (default: input_file.gif)')
    parser.add_argument('-s', '--scale', type=int, default=75,
                        help='Scale percentage (default: 75)')
    parser.add_argument('-x', '--speed', type=float, default=2.0,
                        help='Speed multiplier (default: 2.0 for 2x speed)')
    parser.add_argument('-f', '--fps', type=int, default=10,
                        help='Output frame rate (default: 10)')
    parser.add_argument('--no-optimize', action='store_true',
                        help='Skip GIF optimization step')
    
    args = parser.parse_args()
    
    # Check dependencies first
    check_dependencies()
    
    # Convert
    mov_to_gif(
        args.input,
        args.output,
        args.scale,
        args.speed,
        args.fps,
        optimize=not args.no_optimize
    )


if __name__ == '__main__':
    main()