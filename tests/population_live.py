"""Capture actual 5200 cartridge populations with normal spawning and motion.

Stage advancement is a fixture. It clears the previous wave and waits for the
game's own wave_reset; it never injects enemy counts, positions, or artwork in
the new wave. Invulnerability holds the flock steady while fire stays released.
Pass the actual user-facing .car, not an independently built model ROM.
"""
from pathlib import Path
import argparse, hashlib, json, os, re, subprocess, sys, tempfile, time

R = Path(__file__).resolve().parents[1]
p = argparse.ArgumentParser()
p.add_argument('--car', type=Path, required=True)
p.add_argument('--out', type=Path, required=True)
p.add_argument('--samples', type=int, default=160)
args = p.parse_args()
car = args.car.resolve(); out = args.out.resolve(); out.mkdir(parents=True, exist_ok=True)
S = json.loads((R/'build/symbols.json').read_text())
assert car.read_bytes()[16:] == (R/'build/Phoenix-First-Flight.rom').read_bytes(), 'symbols/model must match the delivered cartridge'
B = Path(os.environ['ALTIRRA_BRIDGE_PACKAGE'])
sys.path.insert(0, str(B/'sdk/python'))
from altirra_bridge import AltirraBridge

with tempfile.TemporaryDirectory(prefix='phoenix-population-') as tmp:
    logpath = Path(tmp)/'emulator.log'
    with logpath.open('w') as log:
        proc = subprocess.Popen([str(B/'AltirraBridgeServer'), '--machine=5200', '--memory=16K', '--bridge=tcp:127.0.0.1:0'], stdout=log, stderr=log, env=dict(os.environ, SDL_AUDIODRIVER='dummy'))
        try:
            for attempt in range(100):
                match = re.search(r'token-file: (\S+)', logpath.read_text())
                if match:
                    try:
                        a = AltirraBridge.from_token_file(match[1]); break
                    except ConnectionRefusedError:
                        pass
                time.sleep(.05)
            else:
                raise RuntimeError('emulator startup timeout')
            a.pause(); a.config('video', 'ntsc'); a.config('kernel', os.environ['ATARI5200_BIOS'])
            a.boot(str(car)); a.frame(500)
            a.joy(0, fire=True); a.frame(8); a.joy(0, fire=False); a.frame(240)
            rows = []
            for wave in (3, 4, 5):
                a.bp_clear_all(); a.bp_set(S['simulation_update']); a.cycles(240000)
                assert int(a.regs()['PC'][1:], 16) == S['simulation_update']
                a.bp_clear_all()
                setup = dict(wave=wave-1, cycle_stage=wave-2, wave_wait=1, enemy_on=[0]*16,
                    display_enemy_on=[0]*16, aliens_left=0, entrance_timer=0, entrance_handoff=0,
                    wipe_timer=0, state=1, large_mode=0, boss_status=0, boss_entrance_shown=0,
                    shield_pose=255, shield_locked=0, shield_count=0, bomb_on=[0]*5,
                    shot_on=0, second_on=0, invuln=255, lives=3)
                for name, value in setup.items():
                    a.memload(S[name], bytes(value if isinstance(value, list) else [value]))
                for i in range(args.samples):
                    a.poke(S['invuln'], 255); a.frame(20)
                    a.bp_set(S['nmi_handler']); a.cycles(40000)
                    assert int(a.regs()['PC'][1:], 16) == S['nmi_handler']
                    a.bp_clear_all()
                    m = a.memdump(0, 16384)
                    row = dict(wave_requested=wave, sample=i, wave=m[S['wave']], state=m[S['state']],
                        count=m[S['aliens_left']], active=list(m[S['enemy_on']:S['enemy_on']+16]),
                        shown=list(m[S['display_enemy_on']:S['display_enemy_on']+16]),
                        large_x=list(m[S['large_x']:S['large_x']+8]), large_y=list(m[S['large_y']:S['large_y']+8]),
                        enemy_x=list(m[S['enemy_x']:S['enemy_x']+16]), enemy_y=list(m[S['enemy_y']:S['enemy_y']+16]),
                        boss_status=m[S['boss_status']], large_shown=m[S['large_shown']],
                        layout_faults=m[S['layout_faults']])
                    stem = out/f'wave{wave}-{i:02d}'
                    a.screenshot(path=str(stem.with_suffix('.png')))
                    stem.with_suffix('.bin').write_bytes(m)
                    rows.append(row)
                print('wave', wave, 'survivors', rows[-1]['count'], 'layout_faults', rows[-1]['layout_faults'], flush=True)
            report = dict(method=__doc__, car_sha256=hashlib.sha256(car.read_bytes()).hexdigest(), samples=rows)
            (out/'report.json').write_text(json.dumps(report, indent=2))
        finally:
            try:
                a.quit()
            except Exception:
                pass
            try:
                proc.wait(timeout=3)
            except subprocess.TimeoutExpired:
                proc.kill(); proc.wait(timeout=3)
