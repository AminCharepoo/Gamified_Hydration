from machine import Pin
from hx711_gpio import HX711
import time

dt  = Pin(15, Pin.IN)
sck = Pin(14, Pin.OUT)
hx  = HX711(clock=sck, data=dt)

NUM_TRIALS   = 5
KNOWN_WEIGHT = 17  # oz

results = []

print("HX711 Calibration Consistency Test")
print(f"Trials: {NUM_TRIALS}, Known weight: {KNOWN_WEIGHT} oz\n")

for trial in range(1, NUM_TRIALS + 1):
    print(f"--- Trial {trial}/{NUM_TRIALS} ---")
    input("Remove everything from scale, then press Enter to tare...")
    hx.tare(15)
    offset = hx.OFFSET
    print(f"Offset: {offset:.2f}")

    input(f"Place {KNOWN_WEIGHT}oz reference on scale, then press Enter to measure...")
    time.sleep_ms(500)

    raw = hx.read_average(10)
    scale_factor = (raw - offset) / KNOWN_WEIGHT
    print(f"Raw: {raw:.2f}  |  Scale factor: {scale_factor:.4f}\n")

    results.append((offset, scale_factor))

offsets = [r[0] for r in results]
scales  = [r[1] for r in results]
avg_off = sum(offsets) / len(offsets)
avg_sf  = sum(scales)  / len(scales)
dev_off = max(abs(o - avg_off) for o in offsets)
dev_sf  = max(abs(s - avg_sf)  for s in scales)
worst_oz = (dev_sf / avg_sf) * KNOWN_WEIGHT

print("=" * 40)
print(f"{'Trial':<8} {'OFFSET':>12} {'SCALE_FACTOR':>14}")
for i, (o, s) in enumerate(results, 1):
    print(f"  {i:<6} {o:>12.2f} {s:>14.4f}")
print("-" * 40)
print(f"  {'AVG':<6} {avg_off:>12.2f} {avg_sf:>14.4f}")
print(f"  {'MAX DEV':<6} {dev_off:>12.2f} {dev_sf:>14.4f}")
print(f"\nWorst-case weight error: ±{worst_oz:.3f} oz")
print("=" * 40)

if dev_off < 500 and worst_oz < 0.5:
    print("\n CONSISTENT - safe to hardcode:")
    print(f"  TARE_OFFSET  = {avg_off:.2f}")
    print(f"  scale_factor = {avg_sf:.4f}")
else:
    print("\n INCONSISTENT - keep calibrating on boot.")