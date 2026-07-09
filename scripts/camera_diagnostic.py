#!/usr/bin/env python3
"""
Camera Diagnostic Tool
======================
Scans all camera indices with multiple backends to find
virtual cameras (Camo Studio, OBS, etc.) and physical webcams.
"""
import cv2
import sys


def test_camera(index, backend=None, backend_name='default'):
    """Test a single camera with a given backend."""
    if backend is not None:
        cap = cv2.VideoCapture(index, backend)
    else:
        cap = cv2.VideoCapture(index)

    if not cap.isOpened():
        cap.release()
        return None

    # Read a few frames to check if the camera actually delivers
    frames_ok = 0
    for _ in range(5):
        ret, frame = cap.read()
        if ret and frame is not None and frame.mean() > 10:  # not black
            frames_ok += 1

    w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    cap.release()

    if frames_ok > 0:
        return {
            'index': index,
            'backend': backend_name,
            'resolution': f'{w}x{h}',
            'fps': fps,
            'working': True,
            'frames_ok': frames_ok,
        }
    else:
        return {
            'index': index,
            'backend': backend_name,
            'resolution': f'{w}x{h}',
            'fps': fps,
            'working': False,
            'note': 'Opens but delivers black frames — may be a virtual camera needing activation',
        }


def main():
    print('=' * 60)
    print('  CAMERA DIAGNOSTIC TOOL')
    print('=' * 60)
    print()
    print('Scanning cameras 0-9 with all backends...')
    print()

    backends = [
        (cv2.CAP_DSHOW, 'DSHOW'),
        (None, 'default'),
        (cv2.CAP_MSMF, 'MSMF'),
    ]

    all_results = []

    for idx in range(10):
        for backend, name in backends:
            result = test_camera(idx, backend, name)
            if result:
                all_results.append(result)
                if result['working']:
                    print(f"  ✅ Camera {idx} [{name:8s}] {result['resolution']:10s} — WORKING ({result['frames_ok']}/5 frames)")
                else:
                    print(f"  ⚠️  Camera {idx} [{name:8s}] {result['resolution']:10s} — {result['note']}")

    print()
    print('=' * 60)
    print('  SUMMARY')
    print('=' * 60)

    working = [r for r in all_results if r['working']]
    virtual = [r for r in all_results if not r['working']]

    if working:
        print(f'\n✅ WORKING CAMERAS ({len(working)}):')
        for r in working:
            print(f'   Camera {r["index"]} [{r["backend"]}] — {r["resolution"]} — use: python -m app.main {r["index"]}')

    if virtual:
        print(f'\n⚠️  VIRTUAL CAMERAS — OPEN BUT BLACK ({len(virtual)}):')
        for r in virtual:
            print(f'   Camera {r["index"]} [{r["backend"]}] — {r["resolution"]}')
        print('\n   💡 TIPS for virtual cameras (Camo Studio, OBS, etc.):')
        print('      - Make sure the app is running and streaming on your iPhone')
        print('      - In Camo Studio on Windows: check "Virtual Camera" is ON')
        print('      - Try reconnecting the USB cable')
        print('      - Restart Camo Studio on both devices')

    if not working and not virtual:
        print('\n❌ No cameras detected at all.')

    print()
    print('To use with detection:')
    print('   python -m app.main <camera_index>')
    print()


if __name__ == '__main__':
    main()
