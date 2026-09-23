// Time of day from the game clock (minutes since midnight). Kept free of Phaser so data
// modules and Node tools can use it.
export function timeOfDay(minute) {
  const m = ((minute % 1440) + 1440) % 1440;
  if (m >= 300 && m < 420) { return 'dawn'; }
  if (m >= 420 && m < 1080) { return 'day'; }
  if (m >= 1080 && m < 1200) { return 'dusk'; }
  return 'night';
}
