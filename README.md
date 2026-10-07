# 2048: Your Rules

A touch-friendly 2048-style game made with Python and Kivy. Choose a starting number from 1 to 9, then combine equal tiles to double their value. For example, base 7 makes the chain 7, 14, 28, 56, and so on. The goal scales with the chosen base: `base x 1024`.

## Desktop

Install Python 3.10 or newer, then run:

```sh
python -m pip install -r requirements.txt
python main.py
```

Use the arrow keys or WASD to move. On a touchscreen, swipe in the direction you want to move. Choose a starting number from 1 through 9 and press **NEW GAME** to restart with that number. **UNDO** takes back the last move. **EXIT** closes the game.

Use **?** for the rules. Restart and exit ask before clearing the current game. To add custom behavior, edit the marked `CUSTOM LOGIC HOOKS` section in `main.py`; it provides hooks for new games, move directions (`up`, `down`, `left`, `right`), and exit. Replace `pass` with your code; by default the hooks do nothing.

## Android and ads

Build with Buildozer from Linux or WSL. Install Buildozer and its Android dependencies, then run:

```sh
buildozer android debug
```

The included `buildozer.spec` targets API 36 for current Google Play submissions. Change `package.domain` and `package.name` to a unique app ID before publishing.

On Android, the game loads an AdMob banner and requests an interstitial after a win or when no moves remain, then automatically starts a new game after a short pause. Reaching the target ends that game. On desktop, a new game starts without an ad. It currently uses Google's test IDs in [ads_config.py](ads_config.py) and `buildozer.spec`; test ads do not earn revenue. Before release, create an AdMob app and ad units, then replace those IDs with your own. Keep test IDs during development and don't click production ads. Google's [test ads guide](https://developers.google.com/admob/android/test-ads) explains safe testing.
