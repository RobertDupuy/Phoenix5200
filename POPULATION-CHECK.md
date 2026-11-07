# 5200 population verification — 6 November 2026

Cartridge SHA-256: `8a157fbc2d12bbea76719f3a92c96a5cf4355c0a5afe82fe9a6000be68699cd3`.

This cartridge retains the v0.31 populations: seven large birds in both large
waves and five mothership escorts. Actual Altirra ANTIC screenshots show all
seven and all five, not merely counters read from RAM.

The earlier saved 5200 cartridge with SHA-256
`698bc3c5855e4394e4850b1a778ec28243fd7b16a7ffed367b00d3781bbdc923`
was the six/four build. Its source sets six large birds and disables records
6 and 7, and sets `escort_population` to 4. It is not the cartridge in this
package.

`tests/population_live.py --car Phoenix5200.car --out evidence/population-final`
loads the delivered cartridge itself using an original 5200 BIOS. The test
advances to each wave and then lets the game spawn and move its own enemies;
it does not inject replacement counts, positions, artwork, or motion. Fire
is released, and invulnerability preserves the flock. This is a staged test,
not a controller-only playthrough.

The included report covers 160 samples per wave, each separated by 20 video
frames and a VBI boundary. The selected actual screenshots are:

- `evidence/population-final/wave3-128.png`: seven large birds.
- `evidence/population-final/wave4-128.png`: seven large birds.
- `evidence/population-final/wave5-10.png`: five escorts above the mothership.

All three runs end with the expected population and zero layout faults.
The build now checks the seven/five constants in the resident and campaign
banks, and packaging checks that the source archive's CAR matches the download.
