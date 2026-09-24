// Player looks, chosen at the start. Boys and girls each have four.
export const PLAYER_STYLES = ['player_a', 'player_b', 'player_c', 'player_d', 'player_e', 'player_f', 'player_g', 'player_h'];
export const PLAYER_SEX = ['m', 'f', 'm', 'f', 'm', 'f', 'm', 'f'];
export const STYLES_FOR = {
  m: PLAYER_STYLES.map((s, i) => i).filter((i) => PLAYER_SEX[i] === 'm'),
  f: PLAYER_STYLES.map((s, i) => i).filter((i) => PLAYER_SEX[i] === 'f'),
};
export function playerStyleKey(style) { return PLAYER_STYLES[style] || PLAYER_STYLES[0]; }
