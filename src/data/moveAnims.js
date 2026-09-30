// Which animation and sounds each move plays (see battle/moveFx.js for the effects themselves).
//
// Common moves share a recipe by kind (tackle, bite, beam, wave...), coloured by the move's type,
// with the type's sound layered on contact moves. Signature moves — every move that only one Morph
// line can learn (starters, evolved signatures, the mythical Twinklit line, Tiamat…) — have their own
// hand-made recipe and their own sound (sig_<move>.ogg), so they never look or sound like the rest.
import { MOVES } from './moves.js';

// ── step helpers ─────────────────────────────────────────────────────────
const st = (op) => (o = {}) => ({ op, ...o });
const P = (s) => ({ ...s, par: true });
const lunge = st('lunge'), hop = st('hop'), spin = st('spin'), wobble = st('wobble'), squash = st('squash'), dive = st('dive');
const glow = st('glow'), fade = st('fade'), shake = st('shake'), flash = st('flash'), tint = st('tint');
const proj = st('projectile'), stream = st('stream'), beam = st('beam'), bolt = st('bolt'), burst = st('burst'), impact = st('impact');
const hit = st('hit'), slash = st('slash'), jaws = st('jaws'), fall = st('fall'), rise = st('rise'), rings = st('rings'), wave = st('wave');
const swirl = st('swirl'), rain = st('rain'), cloud = st('cloud'), drain = st('drain'), float = st('float'), sparkle = st('sparkle');
const arrows = st('arrows'), shield = st('shield'), show = st('show'), streak = st('streak'), gather = st('gather'), wait = st('wait');
const sfx = (key, o = {}) => ({ op: 'sfx', key, ...o });
const S = (key, o = {}) => P(sfx(key, o));

// Sound layered on contact hits so a fire bite sounds hot, a steel ram clangs, etc.
export const TYPE_SFX = {
  Ember: 'mv_fire', Tide: 'mv_water', Static: 'mv_zap', Frost: 'mv_ice', Nature: 'mv_leaf', Toxin: 'mv_poison', Umbra: 'mv_shadow',
  Mind: 'mv_psychic', Iron: 'mv_metal', Stone: 'mv_rock', Wing: 'mv_wing', Drake: 'mv_dragon', Fae: 'mv_fae', Swarm: 'mv_buzz',
};
const typed = (t, vol = 0.55) => (TYPE_SFX[t] ? [S(TYPE_SFX[t], { vol })] : []);
const VOLLEY_KEY = { Nature: 'fx_seed', Swarm: 'fx_needle', Static: 'fx_needle', Frost: 'fx_icicle', Iron: 'fx_cog', Stone: 'fx_rock1' };
const FALL_KEYS = { Frost: ['fx_icicle'], Iron: ['fx_cog', 'fx_rock2'], Nature: ['fx_leaf'] };

// ── shared recipes for common moves ──────────────────────────────────────
export const KINDS = {
  tackle: (t) => [S('mv_tackle'), lunge({ dist: 34, ms: 120 }), P(impact({})), burst({ count: 10, color: t === 'Plain' ? 0xffffff : undefined }), ...typed(t)],
  quick: (t) => [S('mv_tackle', { rate: 1.3 }), P(streak({ count: 3 })), lunge({ dist: 40, ms: 80 }), impact({ scale: 1 }), ...typed(t, 0.4)],
  heavy: (t) => [hop({ h: 26, ms: 170 }), lunge({ dist: 44, ms: 140 }), S('mv_heavy'), P(shake({ amp: 0.016, ms: 320 })), impact({ scale: 2 }), burst({ count: 20, speed: 95 }), ...typed(t)],
  punch: (t) => [lunge({ dist: 16, ms: 80 }), S('mv_punch'), hit({ key: 'fx_fist' }), ...typed(t, 0.45)],
  kick: (t) => [lunge({ dist: 18, ms: 90 }), S('mv_kick'), hit({ key: 'fx_foot', scale: 1.8 }), ...typed(t, 0.45)],
  uppercut: (t) => [lunge({ dist: 20, ms: 90 }), S('mv_punch', { rate: 0.85 }), P(hop({ who: 'foe', h: 10, ms: 120 })), hit({ key: 'fx_fist', scale: 2 }), burst({ count: 8, speed: 60 }), ...typed(t, 0.45)],
  slash: (t) => [S('mv_slash'), slash({ count: 2, cross: true }), ...typed(t, 0.4)],
  claw: (t) => [S('mv_claw'), slash({ key: 'fx_claw', scale: 1.8, angle: 0 }), burst({ count: 8, speed: 50 }), ...typed(t, 0.4)],
  bite: (t) => [lunge({ dist: 14, ms: 80 }), S('mv_bite'), jaws({}), burst({ count: 8, speed: 50 }), ...typed(t, 0.5)],
  sting: (t) => [lunge({ dist: 14, ms: 70 }), S('mv_sting'), proj({ key: 'fx_needle', ms: 140, scale: 2 }), impact({ scale: 0.9 }), ...typed(t, 0.35)],
  volley: (t) => [S('mv_sting', { rate: 0.9 }), proj({ key: VOLLEY_KEY[t] || 'fx_orb', count: 2, ms: 180, stagger: 50, scale: 1.6, add: false }), P(impact({ scale: 0.8 })), ...typed(t, 0.3)],
  whip: (t) => [S('mv_whip'), slash({ key: 'fx_slash', angle: 12, scale: 2.2 }), burst({ count: 8 }), ...typed(t, 0.4)],
  wing: (t) => [S('mv_wing'), P(swirl({ key: 'fx_feather', count: 6, radius: 30, ms: 380, at: 'user', close: false, color: 0xffffff })), lunge({ dist: 30 }), slash({ angle: -10, scale: 1.8 }), ...typed(t, 0.3)],
  dive: (t) => [S('mv_dive'), dive({}), P(shake({ amp: 0.012 })), impact({ scale: 1.8 }), burst({ count: 16, speed: 90 }), ...typed(t, 0.4)],
  quake: (t) => [S('mv_quake'), P(shake({ amp: 0.02, ms: 650 })), rise({ key: 'fx_rock1', count: 5, h: 26, color: false }), burst({ key: 'p_sq', count: 18, speed: 80, gravity: 220, color: 'dark' })],
  rockfall: (t) => [S('mv_rock'), fall({ keys: FALL_KEYS[t] || ['fx_rock0', 'fx_rock1', 'fx_rock2'], count: 5, color: FALL_KEYS[t] ? undefined : false }), P(shake({ amp: 0.012 })), burst({ key: 'p_sq', count: 12, gravity: 200, color: 'dark' })],
  throw: (t) => [S('mv_throw'), proj({ key: t === 'Stone' ? 'fx_rock0' : 'fx_orb', arc: 34, ms: 380, scale: 1.8, spin: 1.5, add: false, color: t === 'Stone' ? false : undefined }), S('mv_rock', { vol: 0.6 }), burst({ key: 'p_sq', count: 10, gravity: 180 })],
  orb: (t) => [S('mv_orb'), gather({ count: 8, ms: 260 }), proj({ scale: 2.2, ms: 320 }), burst({ count: 16, speed: 80 }), ...typed(t, 0.4)],
  beam: (t) => [gather({ ms: 300 }), S('mv_beam'), beam({ w: 8 }), burst({ count: 14, speed: 70 })],
  flame: () => [S('mv_fire'), stream({ key: 'fx_flame', scale: 1.4, add: false }), burst({ key: 'p_dot', count: 14, speed: 60 })],
  fireblast: () => [S('mv_fire'), proj({ key: 'fx_orb', scale: 2.4, ms: 300 }), P(flash({ color: 0xff8a3a, alpha: 0.35 })), rise({ key: 'fx_flame', count: 6, h: 40 }), burst({ count: 16 })],
  water: () => [S('mv_water'), stream({ key: 'fx_bubble', scale: 1.3, add: false }), burst({ key: 'fx_bubble', count: 12, speed: 70, gravity: 150, scale: 1 })],
  wave: () => [S('mv_wave'), wave({})],
  bubble: () => [S('mv_bubble'), proj({ key: 'fx_bubble', count: 6, arc: 18, ms: 420, stagger: 70, scale: 1.6, add: false }), burst({ key: 'fx_bubble', count: 8, scale: 0.9 })],
  bolt: () => [P(flash({ color: 0xffffff, alpha: 0.5 })), S('mv_bolt'), bolt({}), burst({ count: 14, speed: 80 }), wobble({ ms: 240 })],
  zap: () => [S('mv_zap'), bolt({ from: 'user', width: 2, ms: 220 }), burst({ key: 'p_star', count: 10, speed: 50 }), wobble({ ms: 200, amp: 3 })],
  ice: () => [S('mv_ice'), proj({ key: 'fx_icicle', count: 3, ms: 260, stagger: 60, scale: 1.6, add: false }), burst({ key: 'p_snow', count: 14, speed: 60 })],
  blizzard: () => [S('mv_wind'), S('mv_ice', { vol: 0.6 }), P(tint({ color: 0xbfe8ff, alpha: 0.25, ms: 800 })), rain({ key: 'p_snow', count: 40, area: 'screen', angle: 0.6, ms: 800 }), burst({ key: 'p_snow', count: 16 })],
  gust: () => [S('mv_wind'), P(swirl({ key: 'p_ring', count: 8, radius: 26, ms: 420, at: 'mid', close: false, add: true })), proj({ key: 'fx_slash', count: 2, ms: 260, stagger: 80, scale: 1.4 }), burst({ count: 10 })],
  leaves: () => [S('mv_leaf'), swirl({ key: 'fx_leaf', count: 12, radius: 44, ms: 700 }), burst({ key: 'fx_leaf', count: 10, scale: 1.2 })],
  psychic: () => [S('mv_psychic'), P(tint({ color: 0xff7ab8, alpha: 0.22, ms: 700 })), rings({ count: 4, to: 4.5 }), wobble({ ms: 360 })],
  shadow: () => [S('mv_shadow'), P(tint({ color: 0x100818, alpha: 0.45, ms: 760 })), cloud({ color: 'dark', count: 8, scale: 0.55 }), fade({ to: 0.35 })],
  poison: () => [S('mv_poison'), proj({ key: 'fx_orb', count: 3, arc: 26, ms: 360, stagger: 70, scale: 1.8, add: false }), burst({ key: 'p_dot', count: 14, gravity: 160, speed: 60 })],
  powder: () => [S('mv_powder'), cloud({ count: 10, scale: 0.5 }), P(burst({ key: 'p_dot', count: 10, speed: 30 }))],
  sound: () => [S('mv_sound'), rings({ at: 'user', count: 3, to: 3, color: 0xffffff }), P(float({ key: 'fx_note', count: 3, at: 'foe' })), wobble({ ms: 260, amp: 4 })],
  roar: () => [S('mv_sound', { rate: 0.8 }), rings({ at: 'user', count: 3, to: 3.5, color: 0xffffff }), arrows({ who: 'foe', dir: 'down', color: 0x8ab8ff })],
  cry: () => [S('mv_sound', { rate: 1.2 }), rings({ at: 'user', count: 2, to: 3, color: 0xffd65c }), S('mv_buff'), arrows({ who: 'user', dir: 'up', color: 0xffd65c })],
  drain: () => [S('mv_drain'), burst({ count: 8, speed: 40 }), drain({}), glow({ who: 'user', color: 0x8aff8a, pulses: 1 })],
  breath: () => [S('mv_breath'), stream({ key: 'fx_orb', count: 18, scale: 1.2, spread: 16, grow: 1 }), burst({ count: 14 })],
  nova: () => [S('mv_charge'), gather({ ms: 380, count: 16 }), S('mv_nova'), P(flash({ alpha: 0.7 })), P(shake({ amp: 0.02, ms: 400 })), rings({ at: 'foe', count: 4, to: 7, gap: 60 }), burst({ count: 24, speed: 120 })],
  fae: () => [S('mv_fae'), sparkle({ count: 12 }), float({ key: 'fx_heart', count: 3 })],
  buff: () => [S('mv_buff'), glow({ who: 'user', pulses: 2 }), arrows({ who: 'user', dir: 'up' })],
  debuff: () => [S('mv_debuff'), arrows({ who: 'foe', dir: 'down' })],
  gaze: () => [P(tint({ color: 0x000000, alpha: 0.3, ms: 520 })), S('mv_shadow', { vol: 0.5, rate: 1.4 }), glow({ who: 'foe', color: 'dark', pulses: 1 }), S('mv_debuff'), arrows({ who: 'foe', dir: 'down' })],
  heal: () => [S('mv_heal'), P(rings({ at: 'user', count: 2, to: 3, color: 0x8aff8a })), sparkle({ at: 'user', count: 12, color: 0x8aff8a })],
  protect: () => [S('mv_protect'), shield({})],
  sleep: () => [S('mv_sleep'), rings({ count: 2, to: 3, ms: 700, color: 0xd8c8ff }), float({ key: 'fx_z', count: 3, color: 0xffffff })],
  confuse: () => [S('mv_psychic', { rate: 1.3 }), beam({ w: 5, color: 0xff9ad0 }), wobble({ ms: 420 }), float({ key: 'fx_sparkle', count: 3 })],
  seed: () => [S('mv_seed'), proj({ key: 'fx_seed', count: 3, arc: 30, ms: 380, stagger: 60, add: false, color: false }), rise({ key: 'fx_leaf', count: 4, h: 18 })],
  silk: () => [S('mv_silk'), proj({ key: 'fx_web', ms: 320, scale: 1, grow: 1.5, add: false, color: 0xffffff }), arrows({ who: 'foe', dir: 'down', color: 0xffffff })],
};

// Every common move → kind.
export const MOVE_KIND = {
  bump: 'tackle', nip: 'bite', flit_strike: 'quick', gruff_bark: 'roar', stern_look: 'gaze', ram_charge: 'heavy',
  rally_cry: 'cry', mend: 'heal', brace: 'buff', lullaby: 'sleep', grand_slam: 'heavy', guard_up: 'protect', flail_out: 'tackle',
  leaf_nick: 'slash', heal_bud: 'heal', drowse_pollen: 'powder', sap_drain: 'drain', bloom_blast: 'leaves',
  ember_spark: 'flame', blaze_ring: 'fireblast', splash_drop: 'water', tide_pulse: 'wave', brine_fang: 'bite', undertow: 'wave',
  hydro_burst: 'water', tidal_guard: 'buff', static_jolt: 'zap', charge_ram: 'tackle', numb_pulse: 'zap', thunder_arc: 'bolt',
  skybolt: 'bolt', overcharge: 'buff', stone_toss: 'throw', grit_spray: 'powder', rubble_fall: 'rockfall', quake_stomp: 'quake',
  mountain_crash: 'heavy', boulder_drop: 'rockfall', stoneskin: 'buff', chill_nip: 'ice', icicle_jab: 'sting', hail_volley: 'volley',
  rime_ray: 'beam', whiteout_gale: 'blizzard', beak_jab: 'sting', breeze_cut: 'gust', wing_strike: 'wing', gale_slice: 'gust',
  sky_dive: 'dive', updraft: 'buff', tempest_wing: 'gust', mandible_nip: 'bite', pin_volley: 'volley', silk_snare: 'silk',
  sap_sting: 'sting', scythe_rend: 'slash', swarm_strike: 'tackle', drone_hum: 'sound', chitin_guard: 'buff', acid_spit: 'poison',
  toxic_fang: 'bite', corrode: 'debuff', blight_cloud: 'powder', noxious_jab: 'sting', venom_lash: 'whip', toxic_torrent: 'wave',
  mire_blast: 'poison', palm_strike: 'punch', counterblow: 'punch', knuckle_barrage: 'punch', power_kick: 'kick', all_out_slam: 'heavy',
  rising_uppercut: 'uppercut', battle_stance: 'buff', psy_blast: 'psychic', daze_beam: 'confuse', trance: 'sleep', mind_spike: 'psychic',
  psi_horn: 'sting', astral_ray: 'beam', clear_thought: 'buff', shade_fang: 'bite', night_tremor: 'shadow', ambush: 'quick',
  shadow_creep: 'shadow', hex_mist: 'powder', dread_gaze: 'gaze', nightrend: 'claw', chrome_claw: 'claw', cog_strike: 'volley',
  alloy_lash: 'whip', plate_up: 'buff', steel_ram: 'heavy', anvil_drop: 'rockfall', wyrm_breath: 'breath', scale_rake: 'claw',
  coil_whip: 'whip', draconic_surge: 'buff', rift_nova: 'nova',
};

// ── one-of-a-kind recipes: every move only one Morph line learns ─────────
const sig = (id) => S(`sig_${id}`);
const PINK = 0xff9ad0, GOLD = 0xffd65c, MOON = 0xfff4c0, NIGHT = 0x201830, EMBER = 0xff7a3d, TEAL = 0x6fe0c8;
export const SIGNATURE = {
  // Twinklit → Lumelynx → Seraphelis (Mind/Fae, mythical)
  dream_tap: [sig('dream_tap'), show({ key: 'fx_orb', at: 'user', dy: -18, scale: 0.6, color: PINK, add: true, ms: 220, to: { scale: 1.4 } }), proj({ key: 'fx_orb', color: PINK, ms: 420, scale: 1.2 }), P(float({ key: 'fx_z', count: 1, color: 0xffffff })), impact({ color: PINK, scale: 0.9 })],
  glimmer_kiss: [sig('glimmer_kiss'), float({ key: 'fx_heart', at: 'user', count: 2, color: PINK, ms: 400 }), proj({ key: 'fx_heart', count: 3, arc: 22, ms: 420, stagger: 90, color: PINK, add: false, rotate: false }), sparkle({ count: 8, color: PINK })],
  starlight_purr: [sig('starlight_purr'), rings({ at: 'user', count: 3, to: 3, color: PINK, ms: 700, gap: 160 }), float({ key: 'fx_sparkle', at: 'user', count: 5, color: MOON }), arrows({ who: 'foe', dir: 'down', color: PINK })],
  mind_ripple: [sig('mind_ripple'), rings({ at: 'user', count: 2, to: 2.5 }), rings({ at: 'mid', count: 2, to: 3.5 }), rings({ at: 'foe', count: 5, to: 5, gap: 70 }), wobble({ ms: 420 })],
  moonbeam_pounce: [sig('moonbeam_pounce'), P(tint({ color: NIGHT, alpha: 0.4, ms: 900 })), show({ key: 'fx_orb', at: 'sky', dy: 40, scale: 2.5, color: MOON, add: true, ms: 300 }), beam({ from: 'sky', to: 'foe', w: 14, color: MOON, ms: 380 }), dive({ color: MOON }), impact({ color: MOON, scale: 2 }), sparkle({ count: 8, color: MOON })],
  psyche_bloom: [sig('psyche_bloom'), swirl({ key: 'fx_leaf', at: 'user', count: 10, color: PINK, close: false, radius: 34, ms: 700 }), P(rings({ at: 'user', count: 2, to: 3, color: PINK })), arrows({ who: 'user', dir: 'up', color: PINK })],
  fae_ring: [sig('fae_ring'), swirl({ key: 'fx_sparkle', count: 14, color: PINK, close: false, radius: 40, spin: 2.5, ms: 900, add: true }), P(flash({ color: PINK, alpha: 0.3 })), burst({ key: 'fx_sparkle', count: 14, speed: 90 })],
  wishing_star: [sig('wishing_star'), show({ key: 'fx_sparkle', at: 'user', dy: -46, scale: 1, color: MOON, add: true, ms: 360, to: { scale: 4, angle: 180 } }), rain({ key: 'fx_sparkle', count: 14, color: MOON, ms: 600, scale: 0.9 }), sparkle({ at: 'user', count: 12, color: 0x8aff8a })],
  astral_purr: [sig('astral_purr'), P(tint({ color: 0x0a0a30, alpha: 0.5, ms: 1100 })), rain({ key: 'fx_sparkle', area: 'screen', count: 30, color: MOON, angle: 0, ms: 800, scale: 0.8 }), rings({ at: 'user', count: 2, to: 3 }), rings({ at: 'foe', count: 3, to: 6, color: 0xb8a8ff }), shake({ amp: 0.006 })],
  dreamshatter: [sig('dreamshatter'), P(tint({ color: 0xff7ab8, alpha: 0.35, ms: 900 })), float({ key: 'fx_z', count: 3, color: 0xffffff, ms: 400 }), flash({ alpha: 0.9 }), P(shake({ amp: 0.018, ms: 360 })), burst({ key: 'p_sq', count: 30, speed: 130, color: [0xffffff, PINK, 0xb8a8ff], scale: 2.4 }), wobble({ ms: 400 })],
  aurora_benediction: [sig('aurora_benediction'), rain({ key: 'p_rain', area: 'screen', count: 36, color: [0x8affc8, PINK, 0x8ab8ff], angle: 0.1, ms: 800 }), beam({ w: 10, color: 0x8affc8, color2: PINK }), drain({ color: 0x8affc8 }), sparkle({ at: 'user', count: 10, color: PINK })],
  lullaby_siphon: [sig('lullaby_siphon'), P(tint({ color: NIGHT, alpha: 0.4, ms: 1300 })), float({ key: 'fx_note', at: 'user', count: 4, color: PINK, ms: 520 }), rings({ at: 'foe', count: 3, to: 3.5, color: 0xd8c8ff, ms: 700, gap: 140 }), P(float({ key: 'fx_z', count: 3, color: 0xffffff })), drain({ key: 'fx_sparkle', color: PINK }), glow({ who: 'user', color: PINK, pulses: 1 })],
  cosmic_insight: [sig('cosmic_insight'), P(tint({ color: 0x0a0418, alpha: 0.6, ms: 1500, hold: 700 })), gather({ ms: 520, count: 20, radius: 80, color: 0xb8a8ff }), rings({ at: 'user', count: 3, to: 4, gap: 60, color: PINK }), beam({ w: 16, color: 0xb8a8ff, color2: 0xffffff, ms: 560 }), P(flash({ alpha: 0.9 })), P(shake({ amp: 0.024, ms: 500 })), burst({ key: 'fx_sparkle', count: 30, speed: 140 })],
  // Spriglet line
  sprout_tackle: [sig('sprout_tackle'), hop({ h: 14, ms: 110 }), lunge({ dist: 34 }), P(impact({ color: 0x8adc5a })), burst({ key: 'fx_leaf', count: 8, color: 0x8adc5a, scale: 1.2 })],
  petal_cloak: [sig('petal_cloak'), swirl({ key: 'fx_leaf', at: 'user', count: 12, color: [PINK, 0x8adc5a], close: false, radius: 30, spin: 2, ms: 760 }), shield({ color: 0x8adc5a }), arrows({ who: 'user', dir: 'up', color: 0x8adc5a })],
  bramble_whip: [sig('bramble_whip'), slash({ key: 'fx_slash', angle: 20, scale: 2, count: 2, color: 0x4a8a2a }), burst({ key: 'fx_leaf', count: 10, color: 0x6aba4a, scale: 1.1 }), burst({ key: 'p_star', count: 6, color: 0xc8a86a, speed: 40 })],
  pebble_seed: [sig('pebble_seed'), proj({ key: 'fx_seed', arc: 26, ms: 300, add: false, color: false, scale: 1.8 }), P(impact({ color: 0xb38b5d, scale: 1 })), burst({ key: 'fx_rock1', count: 6, gravity: 220, color: false, scale: 0.8 })],
  verdant_pulse: [sig('verdant_pulse'), rings({ at: 'user', count: 2, to: 2.5, color: 0x8adc5a }), rings({ at: 'foe', count: 3, to: 4, color: 0x5cc15a }), drain({ key: 'fx_leaf', color: 0x8adc5a, scale: 1.2, add: false }), glow({ who: 'user', color: 0x8aff8a, pulses: 1 })],
  rootquake: [sig('rootquake'), P(shake({ amp: 0.018, ms: 600 })), rise({ key: 'fx_icicle', count: 6, h: 38, color: 0x7a5a3a, flip: true }), rise({ key: 'fx_leaf', count: 4, h: 20, color: 0x5cc15a }), burst({ key: 'fx_rock0', count: 8, gravity: 240, color: false, scale: 0.9 })],
  grove_renewal: [sig('grove_renewal'), rain({ key: 'fx_leaf', count: 16, color: 0x8adc5a, ms: 700 }), P(rings({ at: 'user', count: 3, to: 3, color: 0x8aff8a })), sparkle({ at: 'user', count: 14, color: 0xd8ffb0 })],
  ancient_canopy: [sig('ancient_canopy'), P(tint({ color: 0x0a2a10, alpha: 0.5, ms: 1100 })), fall({ keys: ['fx_leaf'], count: 16, color: 0x5cc15a, spread: 60, stagger: 30, scale: 2 }), P(shake({ amp: 0.014, ms: 400 })), burst({ key: 'fx_leaf', count: 20, speed: 110, color: [0x2f7a3a, 0x5cc15a, 0xb8f07a] })],
  monolith_crash: [sig('monolith_crash'), P(tint({ color: 0x2a2018, alpha: 0.3, ms: 900 })), fall({ keys: ['fx_rock2'], count: 1, scale: 5, ms: 520, spread: 0, color: 0x8a8a96 }), P(shake({ amp: 0.03, ms: 520 })), burst({ key: 'fx_rock1', count: 16, gravity: 260, speed: 120, color: false })],
  // Cindlet line
  cinder_pounce: [sig('cinder_pounce'), hop({ h: 18, ms: 120 }), lunge({ dist: 36, ms: 100 }), P(impact({ color: EMBER })), burst({ key: 'p_dot', count: 16, color: [0xffd24a, EMBER, 0xd0302a], gravity: 80 })],
  sulk_smoke: [sig('sulk_smoke'), cloud({ color: [0x5a5a6a, 0x3a3a48, 0x8a8a9a], count: 11, scale: 0.55, alpha: 0.7 }), float({ key: 'fx_orb', count: 4, color: 0x3a3a48, ms: 500, scale: 1 }), arrows({ who: 'foe', dir: 'down', color: 0x9a9aaa })],
  ember_fang: [sig('ember_fang'), lunge({ dist: 14 }), jaws({ color: 0xffb04a }), burst({ key: 'p_dot', count: 14, color: [0xffd24a, EMBER], gravity: -40 }), float({ key: 'fx_flame', count: 2, color: EMBER, ms: 300 })],
  shadow_spark: [sig('shadow_spark'), proj({ key: 'fx_orb', color: NIGHT, add: false, scale: 1.6, ms: 300 }), P(bolt({ from: 'user', width: 1, color: 0xffd24a, ms: 200 })), burst({ count: 12, color: [0x6a54a0, 0xffd24a, NIGHT] })],
  blaze_mane: [sig('blaze_mane'), glow({ who: 'user', color: EMBER, pulses: 2, ms: 300 }), proj({ key: 'fx_flame', count: 6, spread: 26, ms: 340, stagger: 40, add: false, scale: 1.6 }), burst({ key: 'fx_flame', count: 8, speed: 60, scale: 1 })],
  dusk_ignite: [sig('dusk_ignite'), P(tint({ color: NIGHT, alpha: 0.4, ms: 900 })), rise({ key: 'fx_flame', at: 'userGround', count: 5, h: 36, color: 0xa060ff }), rise({ key: 'fx_flame', at: 'userGround', count: 4, h: 24, color: EMBER }), arrows({ who: 'user', dir: 'up', color: 0xa060ff })],
  umbral_flare: [sig('umbral_flare'), stream({ key: 'fx_flame', color: 0x7a4ad0, add: false, scale: 1.5 }), P(flash({ color: NIGHT, alpha: 0.4 })), burst({ key: 'p_dot', count: 16, color: [0x7a4ad0, NIGHT, EMBER] })],
  black_pyre: [sig('black_pyre'), P(tint({ color: 0x000000, alpha: 0.55, ms: 1100 })), rise({ key: 'fx_flame', count: 8, h: 54, color: 0x3a1a5a, scale: 2 }), P(flash({ color: EMBER, alpha: 0.4 })), P(shake({ amp: 0.018, ms: 420 })), burst({ key: 'p_dot', count: 24, color: [0x3a1a5a, 0x7a4ad0, EMBER], speed: 100 })],
  nightfire_rend: [sig('nightfire_rend'), P(tint({ color: NIGHT, alpha: 0.45, ms: 700 })), slash({ key: 'fx_claw', count: 2, cross: true, angle: -20, scale: 2.2, color: 0xb070ff }), burst({ key: 'p_dot', count: 16, color: [EMBER, 0xb070ff] })],
  // Puddlet line
  puddle_hop: [sig('puddle_hop'), hop({ h: 16, ms: 110, times: 2 }), lunge({ dist: 34 }), burst({ key: 'fx_bubble', count: 12, gravity: 180, scale: 1 })],
  drizzle_eyes: [sig('drizzle_eyes'), rain({ key: 'p_rain', count: 20, color: 0x9ad8ff, ms: 700, angle: 0 }), float({ key: 'fx_bubble', count: 2, color: 0x9ad8ff, ms: 500 }), arrows({ who: 'foe', dir: 'down', color: 0x9ad8ff })],
  bubble_snap: [sig('bubble_snap'), proj({ key: 'fx_bubble', count: 5, arc: 10, ms: 300, stagger: 50, add: false, scale: 2 }), P(flash({ color: 0x9ad8ff, alpha: 0.3 })), burst({ key: 'fx_bubble', count: 14, speed: 100, scale: 0.8 })],
  rime_splash: [sig('rime_splash'), stream({ key: 'fx_bubble', count: 8, add: false, scale: 1.2 }), burst({ key: 'p_snow', count: 18, color: [0xffffff, 0x8fe0ff] }), P(glow({ who: 'foe', color: 0x8fe0ff, pulses: 1 }))],
  riptide_fang: [sig('riptide_fang'), wave({ height: 0.6, ms: 500 }), jaws({ color: 0x9ad8ff }), burst({ key: 'fx_bubble', count: 8 })],
  current_coat: [sig('current_coat'), swirl({ key: 'fx_bubble', at: 'user', count: 12, close: false, radius: 32, spin: 2, ms: 760 }), shield({ color: 0x3d8bfd }), arrows({ who: 'user', dir: 'up', color: 0x9ad8ff })],
  glacier_surge: [sig('glacier_surge'), wave({ color: 0x8fe0ff, ms: 620 }), P(shake({ amp: 0.012 })), rise({ key: 'fx_icicle', count: 5, h: 34 })],
  maelstrom: [sig('maelstrom'), P(tint({ color: 0x0a2a5a, alpha: 0.35, ms: 1000 })), swirl({ key: 'fx_bubble', count: 18, radius: 50, spin: 3, ms: 900, close: true }), wave({ ms: 500, height: 0.8 })],
  permafrost_breath: [sig('permafrost_breath'), P(tint({ color: 0x9ad8ff, alpha: 0.3, ms: 900 })), stream({ key: 'p_snow', count: 24, scale: 2.4, spread: 18, grow: 1.5 }), rise({ key: 'fx_icicle', count: 6, h: 40 }), P(glow({ who: 'foe', color: 0x8fe0ff, pulses: 2 }))],
  // Evolved signatures
  eye_of_the_storm: [sig('eye_of_the_storm'), P(tint({ color: 0x1a2030, alpha: 0.5, ms: 1300, hold: 600 })), swirl({ key: 'p_ring', at: 'center', count: 14, radius: 90, spin: 2, ms: 700, close: false, add: true, color: 0xb8c8ff }), P(rain({ key: 'p_rain', area: 'screen', count: 40, angle: 0.5, ms: 700 })), bolt({ count: 2, color: 0xfff27a }), burst({ count: 16, color: [0xb8c8ff, 0xffffff] })],
  thunderwing: [sig('thunderwing'), dive({ color: 0xfff27a }), P(bolt({ count: 1, color: 0xfff27a, ms: 200 })), burst({ key: 'fx_feather', count: 10, color: 0xfff27a, scale: 1.2 }), wobble({ ms: 200 })],
  heartless_night: [sig('heartless_night'), P(tint({ color: 0x000000, alpha: 0.7, ms: 1200, hold: 500 })), cloud({ color: 0x201830, count: 12, scale: 0.7, alpha: 0.8 }), P(sparkle({ count: 8, color: 0x6a54a0 })), fade({ to: 0.15, ms: 500 })],
  riftbreaker: [sig('riftbreaker'), P(shake({ amp: 0.028, ms: 700 })), bolt({ from: 'sky', count: 1, color: TEAL, width: 5 }), rise({ key: 'fx_icicle', count: 7, h: 44, color: TEAL }), P(flash({ color: TEAL, alpha: 0.45 })), burst({ key: 'fx_rock1', count: 14, gravity: 250, color: false, speed: 110 })],
  plague_tide: [sig('plague_tide'), wave({ color: 0x8a3ac8, drops: 'p_dot', height: 1.2 }), cloud({ color: 0x6a2a8a, count: 8, alpha: 0.6 })],
  champions_gauntlet: [sig('champions_gauntlet'), gather({ color: GOLD, ms: 320 }), lunge({ dist: 40, ms: 110 }), hit({ key: 'fx_fist', scale: 2.6, color: GOLD }), P(shake({ amp: 0.02, ms: 300 })), P(impact({ scale: 2.6, color: GOLD })), sparkle({ count: 12, color: GOLD })],
  prophecy_beam: [sig('prophecy_beam'), show({ key: 'fx_orb', at: 'user', dy: -24, color: 0xff7ab8, add: true, scale: 0.4, ms: 260, to: { scale: 1.6 } }), beam({ w: 12, color: 0xff7ab8, color2: 0xfff0fa }), rings({ count: 3, to: 4, color: 0xff7ab8 })],
  aurora_lance: [sig('aurora_lance'), proj({ key: 'fx_icicle', scale: 3.4, ms: 220, add: false }), P(rain({ key: 'p_rain', count: 16, color: [0x8affc8, 0xff9ad0, 0x8fe0ff], angle: 0, ms: 500 })), burst({ key: 'p_snow', count: 20, speed: 110, color: [0x8affc8, 0xff9ad0, 0xffffff] })],
  siege_ram: [sig('siege_ram'), lunge({ dist: 56, ms: 170 }), P(shake({ amp: 0.024, ms: 380 })), impact({ scale: 2.4, color: 0xd0d8e8 }), burst({ key: 'fx_cog', count: 8, gravity: 220, color: false, speed: 90 })],
  tyrant_skyfall: [sig('tyrant_skyfall'), dive({ color: 0xa080ff, ms: 620 }), P(flash({ color: 0x7a5ae8, alpha: 0.5 })), P(shake({ amp: 0.03, ms: 500 })), rings({ at: 'foeGround', count: 3, to: 6, color: 0x7a5ae8 }), burst({ count: 24, speed: 130 })],
  guillotine_scythe: [sig('guillotine_scythe'), P(tint({ color: 0x000000, alpha: 0.5, ms: 700 })), slash({ angle: -62, scale: 3.4, color: 0xe0ffb0, count: 1 }), flash({ color: 0xe0ffb0, alpha: 0.6 })],
  peakfall: [sig('peakfall'), fall({ keys: ['fx_rock2'], count: 1, scale: 5.5, ms: 560, spread: 0, color: 0xe8f0ff }), P(shake({ amp: 0.03, ms: 560 })), burst({ key: 'p_snow', count: 20, gravity: 120, speed: 120, color: [0xffffff, 0xd8e8ff] }), burst({ key: 'fx_rock0', count: 8, gravity: 260, color: false })],
  siren_sting: [sig('siren_sting'), swirl({ key: 'fx_needle', count: 8, radius: 40, color: 0x9a8aff, close: true, ms: 560, add: true }), P(glow({ who: 'foe', color: 0x9a8aff, pulses: 2 })), burst({ key: 'p_dot', count: 12, color: [0x9a8aff, 0x3d8bfd] })],
  crushing_claw: [sig('crushing_claw'), lunge({ dist: 18 }), jaws({ scale: 2, color: 0xe0603a, ms: 240 }), squash({ amt: 0.3 }), burst({ key: 'fx_rock1', count: 6, color: 0xe0603a, speed: 50 })],
  mammoth_stampede: [sig('mammoth_stampede'), P(shake({ amp: 0.016, ms: 800 })), lunge({ dist: 30, ms: 80 }), lunge({ dist: 36, ms: 80 }), lunge({ dist: 42, ms: 90 }), burst({ key: 'p_sq', count: 22, gravity: 200, color: [0x9a7a5a, 0xc8a878] })],
  tesla_coil: [sig('tesla_coil'), gather({ color: 0xfff27a, ms: 300 }), bolt({ from: 'user', count: 3, color: 0xfff27a, ms: 180 }), P(flash({ color: 0xfff27a, alpha: 0.4 })), burst({ key: 'p_star', count: 18, speed: 100 })],
  glacier_maul: [sig('glacier_maul'), slash({ key: 'fx_claw', scale: 2.6, color: 0xd8f4ff, angle: 10 }), rise({ key: 'fx_icicle', count: 4, h: 30 }), burst({ key: 'p_snow', count: 16 })],
  thunder_jaws: [sig('thunder_jaws'), jaws({ color: 0xfff27a }), P(bolt({ count: 1, width: 2, ms: 200 })), burst({ key: 'p_star', count: 12 })],
  reapers_lantern: [sig('reapers_lantern'), P(tint({ color: 0x000000, alpha: 0.5, ms: 1000 })), show({ key: 'fx_orb', at: 'user', dy: -30, color: TEAL, add: true, scale: 1, ms: 300, to: { scale: 2 } }), drain({ color: TEAL, count: 12 }), glow({ who: 'user', color: TEAL, pulses: 1 })],
  caldera_crush: [sig('caldera_crush'), jaws({ color: 0xff5a2a, scale: 1.8 }), P(shake({ amp: 0.016 })), rise({ key: 'fx_flame', count: 6, h: 40, color: 0xff5a2a }), burst({ key: 'p_dot', count: 16, gravity: 160, color: [0xffd24a, 0xff5a2a, 0x8a2a1a] })],
  death_stinger: [sig('death_stinger'), lunge({ dist: 16 }), proj({ key: 'fx_needle', scale: 3, ms: 160, color: 0xc070ff }), P(impact({ color: 0xc070ff, scale: 1.4 })), cloud({ color: 0x6a2a8a, count: 7, alpha: 0.6 })],
  royal_sting: [sig('royal_sting'), sparkle({ at: 'user', count: 6, color: GOLD, radius: 16 }), proj({ key: 'fx_needle', count: 3, ms: 200, stagger: 60, color: GOLD, scale: 2 }), burst({ key: 'fx_sparkle', count: 10, color: GOLD })],
  moonlit_riddle: [sig('moonlit_riddle'), P(tint({ color: 0x0a1030, alpha: 0.5, ms: 1000 })), show({ key: 'fx_orb', at: 'sky', dy: 44, scale: 2.2, color: MOON, add: true, ms: 360 }), float({ key: 'fx_sparkle', count: 5, color: MOON }), wobble({ ms: 520, amp: 7 })],
  haymaker: [sig('haymaker'), hop({ h: 12 }), spin({ turns: 1, ms: 260 }), lunge({ dist: 38, ms: 100 }), hit({ key: 'fx_fist', scale: 2.8, color: 0xffc0a0 }), P(shake({ amp: 0.022, ms: 300 })), burst({ count: 14, speed: 100 })],
  mycelial_surge: [sig('mycelial_surge'), rise({ key: 'fx_seed', count: 7, h: 26, color: false }), cloud({ color: 0xe8d8a0, count: 12, alpha: 0.6 }), float({ key: 'fx_orb', count: 5, color: 0xf0e070, scale: 0.7 })],
  bulwark_charge: [sig('bulwark_charge'), shield({ color: 0xb8c4d4, ms: 360 }), lunge({ dist: 44, ms: 130 }), impact({ color: 0xd0d8e8, scale: 1.8 }), burst({ key: 'p_sq', count: 12, color: [0xffffff, 0x8e9aaf] })],
  tunnel_quake: [sig('tunnel_quake'), fade({ who: 'user', to: 0, ms: 360 }), P(shake({ amp: 0.022, ms: 700 })), rise({ key: 'fx_rock2', count: 3, h: 30, color: false }), burst({ key: 'fx_rock0', count: 12, gravity: 250, color: false, speed: 110 })],
  dusk_hunt: [sig('dusk_hunt'), fade({ who: 'user', to: 0.1, ms: 220 }), streak({ count: 3, color: 0x6a54a0 }), slash({ key: 'fx_claw', color: 0xb89aff, scale: 2 })],
  primordial_anvil: [sig('primordial_anvil'), P(tint({ color: 0x1a1008, alpha: 0.5, ms: 1500, hold: 700 })), gather({ ms: 480, count: 16, radius: 70, color: 0xffb040 }), fall({ keys: ['fx_rock2'], count: 1, scale: 6, ms: 560, spread: 0, color: 0x6a7488 }), P(shake({ amp: 0.034, ms: 560 })), P(flash({ color: 0xffb040, alpha: 0.5 })), burst({ key: 'fx_cog', count: 10, gravity: 240, speed: 110, color: 0xd09a3c })],
  primordial_tide: [sig('primordial_tide'), P(tint({ color: 0x06204a, alpha: 0.55, ms: 1600, hold: 800 })), wave({ height: 1.6, ms: 700 }), P(shake({ amp: 0.02, ms: 600 })), wave({ height: 1.3, ms: 500, color: TEAL }), rain({ key: 'p_rain', area: 'screen', count: 36, angle: 0.3, ms: 600, color: 0x9ad8ff }), flash({ color: TEAL, alpha: 0.4 })],
  // Other moves only one line learns
  clamor: [sig('clamor'), rings({ at: 'user', count: 4, to: 4, color: 0xffffff, gap: 70 }), P(float({ key: 'fx_note', count: 4, color: 0xffffff })), wobble({ ms: 360, amp: 5 })],
  pummel: [sig('pummel'), lunge({ dist: 12, ms: 60 }), hit({ key: 'fx_fist', scale: 1.2, color: 0xfff0c8, jitter: 18 })],
  vine_lash: [sig('vine_lash'), slash({ key: 'fx_slash', angle: 15, scale: 1.8, color: 0x5cc15a }), burst({ key: 'fx_leaf', count: 6, color: 0x5cc15a, scale: 1 })],
  seed_volley: [sig('seed_volley'), proj({ key: 'fx_seed', count: 2, arc: 12, ms: 200, stagger: 40, add: false, color: false }), impact({ scale: 0.7, color: 0xc8a868 })],
  root_snare: [sig('root_snare'), proj({ key: 'fx_seed', arc: 40, ms: 420, add: false, color: false }), rise({ key: 'fx_leaf', count: 5, h: 22, color: 0x4a8a2a }), glow({ who: 'foe', color: 0x5cc15a, pulses: 2 })],
  timber_crash: [sig('timber_crash'), hop({ h: 30, ms: 180 }), lunge({ dist: 46, ms: 130 }), P(shake({ amp: 0.02, ms: 360 })), burst({ key: 'fx_leaf', count: 12, color: 0x5cc15a }), burst({ key: 'p_sq', count: 12, color: [0x8a5a2a, 0xb87a4a], gravity: 220 })],
  moss_shield: [sig('moss_shield'), cloud({ at: 'user', color: 0x5cc15a, count: 8, alpha: 0.5 }), shield({ color: 0x5cc15a }), arrows({ who: 'user', dir: 'up', color: 0x8adc5a })],
  flare_bite: [sig('flare_bite'), jaws({ color: 0xff5a2a }), P(flash({ color: EMBER, alpha: 0.3 })), burst({ key: 'p_dot', count: 12, color: [0xffd24a, 0xff5a2a] })],
  cinder_claw: [sig('cinder_claw'), slash({ key: 'fx_claw', color: 0xffb04a, scale: 1.8, angle: -15 }), burst({ key: 'p_dot', count: 12, color: [0xffd24a, EMBER], gravity: 90 })],
  inferno_lash: [sig('inferno_lash'), slash({ key: 'fx_slash', angle: 8, scale: 2.8, color: 0xfff0c0 }), rise({ key: 'fx_flame', count: 5, h: 36 }), P(flash({ color: 0xffd24a, alpha: 0.3 }))],
  smoke_veil: [sig('smoke_veil'), cloud({ color: 0x8a8a9a, count: 14, spread: 40, scale: 0.6, alpha: 0.7 }), arrows({ who: 'foe', dir: 'down', color: 0xb8b8c8 })],
  kindle: [sig('kindle'), swirl({ key: 'fx_flame', count: 6, radius: 30, color: 0xa070ff, close: true, ms: 640 }), glow({ who: 'foe', color: EMBER, pulses: 2 })],
  magma_jaws: [sig('magma_jaws'), jaws({ color: 0xd0302a, scale: 1.6 }), P(shake({ amp: 0.01 })), burst({ key: 'p_dot', count: 18, gravity: 200, color: [0xff7a3d, 0xd0302a, 0x3a1a1a] })],
  pyre_rush: [sig('pyre_rush'), streak({ count: 4, color: EMBER }), lunge({ dist: 48, ms: 120 }), P(shake({ amp: 0.016 })), rise({ key: 'fx_flame', count: 6, h: 44 }), burst({ key: 'p_dot', count: 16 })],
  rip_current: [sig('rip_current'), streak({ count: 3, color: 0x9ad8ff }), lunge({ dist: 42, ms: 80 }), burst({ key: 'fx_bubble', count: 10, gravity: 160, scale: 0.9 })],
  volt_fang: [sig('volt_fang'), jaws({ color: 0xfff27a, ms: 150 }), burst({ key: 'p_star', count: 12, speed: 60 }), wobble({ ms: 180, amp: 3 })],
  volt_needle: [sig('volt_needle'), proj({ key: 'fx_needle', ms: 150, color: 0xfff27a, scale: 1.8 }), burst({ key: 'p_star', count: 5, speed: 40 })],
  mud_lob: [sig('mud_lob'), proj({ key: 'fx_orb', arc: 42, ms: 420, color: 0x7a5a3a, add: false, scale: 2.2 }), burst({ key: 'p_dot', count: 16, gravity: 200, color: [0x7a5a3a, 0x5a4028, 0xa88a60] })],
  frost_fang: [sig('frost_fang'), jaws({ color: 0xd8f4ff }), burst({ key: 'p_snow', count: 14 }), P(glow({ who: 'foe', color: 0x8fe0ff, pulses: 1 }))],
  glacial_crush: [sig('glacial_crush'), fall({ keys: ['fx_icicle'], count: 3, scale: 3.2, ms: 420, spread: 18, color: 0xd8f4ff }), P(shake({ amp: 0.016 })), burst({ key: 'p_snow', count: 18, gravity: 140 })],
  frost_armor: [sig('frost_armor'), rise({ key: 'fx_icicle', at: 'userGround', count: 6, h: 30 }), shield({ color: 0x8fe0ff }), arrows({ who: 'user', dir: 'up', color: 0xd8f4ff })],
  psi_wave: [sig('psi_wave'), rings({ at: 'mid', count: 3, to: 3, color: 0xffb0d0, gap: 90 }), rings({ at: 'foe', count: 2, to: 3.5, color: 0xffb0d0 })],
  soul_siphon: [sig('soul_siphon'), fade({ to: 0.4, ms: 300 }), drain({ color: 0xb89aff, count: 10 }), glow({ who: 'user', color: 0xb89aff, pulses: 1 })],
  gleam_cannon: [sig('gleam_cannon'), gather({ color: 0xffffff, ms: 300 }), beam({ w: 12, color: 0xc8d4e8, color2: 0xffffff }), P(flash({ alpha: 0.5 })), burst({ key: 'fx_sparkle', count: 12, color: [0xffffff, 0xc8d4e8] })],
  drake_talon: [sig('drake_talon'), slash({ key: 'fx_claw', count: 2, cross: true, color: TEAL, scale: 2 }), burst({ key: 'fx_sparkle', count: 10, color: [0x7a5ae8, TEAL] })],
  wyvern_dive: [sig('wyvern_dive'), dive({ color: 0x7a5ae8, ms: 560 }), P(shake({ amp: 0.024, ms: 420 })), P(flash({ color: 0x7a5ae8, alpha: 0.4 })), burst({ count: 20, speed: 120 })],
};

// The recipe for a move: its own if it has one, otherwise its kind's (or a sensible default).
export function kindOf(move) {
  if (MOVE_KIND[move.id]) { return MOVE_KIND[move.id]; }
  if (move.cat === 'status') {
    if (move.fx.heal) { return 'heal'; }
    if (move.fx.protect) { return 'protect'; }
    if (move.fx.target === 'self') { return 'buff'; }
    return 'debuff';
  }
  return move.cat === 'phys' ? 'tackle' : 'orb';
}

export function recipeFor(move) {
  if (SIGNATURE[move.id]) { return SIGNATURE[move.id]; }
  const k = KINDS[kindOf(move)] || KINDS.tackle;
  return k(move.type);
}

export function soundsOf(recipe) {
  return recipe.filter((s) => s.op === 'sfx').map((s) => s.key);
}

// every recipe step names an effect that exists (checked by the tests)
export const OPS = ['lunge', 'hop', 'spin', 'wobble', 'squash', 'dive', 'glow', 'fade', 'shake', 'flash', 'tint', 'projectile', 'stream', 'beam',
  'bolt', 'burst', 'impact', 'hit', 'slash', 'jaws', 'fall', 'rise', 'rings', 'wave', 'swirl', 'rain', 'cloud', 'drain', 'float', 'sparkle',
  'arrows', 'shield', 'show', 'streak', 'gather', 'wait', 'sfx'];

export const ALL_MOVES = Object.keys(MOVES);
