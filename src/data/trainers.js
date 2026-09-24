// Every Tamer battle in the game.
// party: [[species, level, moves?], ...]   reward: money per level of their strongest Morph
// skill: 1 ordinary, 2 veteran, 3 Warden/rival/boss.  items: healing items the AI may use once each.
// Text: intro (before), lose (they lost), win (you lost), after (talking to them afterwards).
export const TRAINERS = {};
function t(id, o) { TRAINERS[id] = { id, skill: 1, reward: 24, items: [], ...o }; }
function warden(id, o) { t(id, { title: 'Warden', skill: 3, reward: 110, music: 'battle_trial', bg: 'arena', ...o }); }
function acolyte(id, name, party, o = {}) {
  t(id, {
    title: 'Deepcall Acolyte', name, sprite: o.sprite || 'acolyte', party, reward: 30, skill: 2, music: 'battle_deepcall',
    intro: o.intro || 'The tide is coming back, child. Stand aside or be swept away!',
    lose: o.lose || 'The Mother will not forget this...',
    after: o.after || 'We only want to go home. The whole world was sea, once.',
    ...o,
  });
}

// ── Route 1 ────────────────────────────────────────────────────────────────
t('r1_ollie', { title: 'Youngster', name: 'Ollie', sprite: 'kid', party: [['nibbit', 3]], intro: "I saw you come out of the lab! Let's see what you've got!", lose: 'Aww, my Nibbit!', after: "Keep your Morphs healthy — your mum's cooking works wonders, trust me." });
t('r1_dana', { title: 'Lass', name: 'Dana', sprite: 'lass', party: [['beakling', 3], ['nibbit', 4]], intro: "Eyes on me! My Morphs are the cutest on the whole route!", lose: "Cute AND beaten. Ugh.", after: 'Beaklings peck Nature Morphs to pieces. Just saying!' });
t('r1_theo', { title: 'Tamer', name: 'Theo', sprite: 'youth', party: [['trotter', 5]], intro: "Trotter and I run this route every morning. Let's race!", lose: "We lost the race.", after: 'Brindlewood is just north. The Trial there is tough — train up first.' });
t('r1_nell', { title: 'Bug Fan', name: 'Nell', sprite: 'kid_b', party: [['chittik', 4], ['chittik', 4]], intro: "Shh! You'll scare the Chittiks! ...Too late. BATTLE!", lose: 'My Chittiks!', after: 'Chittiks turn into Mantipules. They get these little boxing gloves. Well, claws.' });

// ── Rival ─────────────────────────────────────────────────────────────────
// Wren always picks the starter that beats yours: {their species}_{stage}
const RIVAL = {
  spriglet: ['cindlet', 'cindreaver', 'pyromane'],
  cindlet: ['puddlet', 'torrentide', 'maelstrand'],
  puddlet: ['spriglet', 'spriggrove', 'mosswarden'],
};
export const RIVAL_PICK = { spriglet: 'cindlet', cindlet: 'puddlet', puddlet: 'spriglet' };
for (const [yours, line] of Object.entries(RIVAL)) {
  const W = line;
  t(`rival1_${yours}`, { title: 'Rival', name: 'Wren', sprite: 'wren', skill: 1, reward: 20, music: 'battle_rival', party: [[W[0], 5, ['bump']]], intro: "Grandma says we're both Tamers now. So let's find out who's better!", lose: "What?! I picked the one with the type advantage!", win: 'Ha! Knew it.' });
  t(`rival2_${yours}`, { title: 'Rival', name: 'Wren', sprite: 'wren', skill: 2, reward: 45, music: 'battle_rival', items: ['tonic'], party: [['beakling', 12], ['pebbling', 12], [W[0], 15]], intro: "Those robed people ran off the second they saw me. Coward cult. Now — rematch!", lose: 'Again?! How are you doing this?', win: "That's more like it." });
  t(`rival3_${yours}`, { title: 'Rival', name: 'Wren', sprite: 'wren', skill: 3, reward: 60, music: 'battle_rival', items: ['strong_tonic'], party: [['skyveer', 25], ['cragmaul', 25], ['voltquill', 24], [W[1], 28]], intro: "Three Sigils. You've got three Sigils and I've got... questions. Battle me. I need to think.", lose: "...Fine. You win. You always win.", win: 'Huh. I needed that.' });
  t(`rival4_${yours}`, { title: 'Rival', name: 'Wren', sprite: 'wren', skill: 3, reward: 90, music: 'battle_rival', items: ['full_tonic', 'full_tonic'], party: [['tempestral', 48], ['cragmaul', 48], ['arcfowl', 49], ['wyrmguard', 48], ['mothlume', 47], [W[2], 52]], intro: 'No cults. No Seals. No grandmas watching. Just you and me — as equals. Ready?', lose: "...Yeah. Yeah, that was the best battle of my life. Thanks, {PLAYER}.", win: "I finally did it! ...It doesn't feel how I thought it would." });
}

// ── Brindlewood Trial ─────────────────────────────────────────────────────
t('bw_adept_1', { title: 'Moss Adept', name: 'Fern', sprite: 'lass', party: [['burrlet', 8], ['chittik', 8]], intro: 'Warden Mossa taught me: a garden is patient. I am... trying to be patient. BATTLE!', lose: 'Patience... failing...', after: 'Mossa is right at the end of the hall. Good luck!' });
t('bw_adept_2', { title: 'Moss Adept', name: 'Rowe', sprite: 'ranger', party: [['sporra', 9], ['burrlet', 9]], intro: 'Roots run deep in this hall. Let me show you!', lose: 'Uprooted!', after: "Mossa's Thornbur is her pride and joy. Watch out for Seed Volley." });
warden('mossa', { name: 'Mossa', sprite: 'mossa', items: ['tonic'], party: [['burrlet', 10], ['sporra', 11, ['bump', 'acid_spit', 'leaf_nick', 'stern_look']], ['thornbur', 12, ['vine_lash', 'leaf_nick', 'brace', 'bump']]], intro: "Welcome to my garden, {PLAYER}. Everything here grows slowly — and hits back hard. Shall we?", lose: 'My, my. You bloomed early.', win: 'Come back when your roots are deeper, dear.' });

// ── Route 2 ───────────────────────────────────────────────────────────────
t('r2_pim', { title: 'Bug Fan', name: 'Pim', sprite: 'kid_b', party: [['chittik', 9], ['fuzzling', 10]], intro: 'I caught a Fuzzling! It is soft AND it will fight you!', lose: 'Soft AND defeated...', after: 'Fuzzlings turn into Mothlumes. They glow! At night! On your pillow!' });
t('r2_fisher', { title: 'Angler', name: 'Doyle', sprite: 'fisher', party: [['pipfrog', 10], ['gullip', 10]], intro: "Nothing's biting. Guess I'll bite YOU. Er. Battle you.", lose: 'Should have stayed fishing.', after: "Can't cross water without a boat. Saltreach sells 'em to Tide Sigil holders." });
t('r2_ivy', { title: 'Lass', name: 'Ivy', sprite: 'lass', party: [['nibbit', 10], ['burrlet', 10], ['beakling', 11]], intro: "You're the one who beat Mossa? Prove it!", lose: 'Okay, okay, I believe you!', after: 'Thornwild is creepy. People in robes have been walking in there all week.' });
t('r2_bram', { title: 'Hiker', name: 'Bram', sprite: 'hiker', party: [['pebbling', 11], ['trotter', 11]], intro: "HOI! Solid as rock, me and my Pebbling! Try us!", lose: 'Crumbled!', after: 'Pebblings evolve into Cragmauls. Big fists. Bigger hugs.' });

// ── Thornwild ────────────────────────────────────────────────────────────
t('tw_bugs', { title: 'Bug Fan', name: 'Rook', sprite: 'kid', party: [['chittik', 11], ['mantipule', 13]], intro: 'Thornwild has the BEST bugs. Want to see my best bug?!', lose: 'My best bug!', after: 'The shrine in the middle of the forest is really old. Older than Brindlewood.' });
t('tw_ranger', { title: 'Ranger', name: 'Sable', sprite: 'ranger', party: [['sporra', 12], ['fuzzling', 12]], intro: 'Rangers keep these woods safe. Show me you can handle yourself.', lose: 'You can handle yourself.', after: 'If you find a lost Burrlet with a bell, it belongs to little Posy in Brindlewood.' });
t('tw_mystic', { title: 'Mystic', name: 'Orla', sprite: 'mystic', party: [['hushling', 13], ['hollowisp', 12]], intro: 'The trees whispered your name. They were not complimentary.', lose: 'The trees were wrong.', after: "Something under the shrine is humming. It's the same note the Seal-stones hum." });
acolyte('tw_acolyte_1', 'Tove', [['oozelet', 12], ['echirp', 12]], { intro: "This shrine belongs to the Mother! Go home, little Tamer.", lose: 'Ugh! Brother, hold the dig!' });
acolyte('tw_acolyte_2', 'Ansel', [['jellume', 13], ['gullip', 12]], { sprite: 'acolyte_b', intro: 'You defeated Tove?! Then the Mother sends ME.', lose: "We'll... we'll finish the dig another day!" });

// ── Saltreach ────────────────────────────────────────────────────────────
acolyte('st_acolyte_1', 'Wick', [['gullip', 15], ['oozelet', 15]], { intro: "This pier is chartered by the Deepcall. Scram!", lose: "Fine! Keep your pier!" });
acolyte('st_acolyte_2', 'Hesk', [['jellume', 16], ['crabbit', 15]], { sprite: 'acolyte_b', intro: "The old man won't sell us his boats. You won't stop us taking them!", lose: 'Retreat! Back to the Riven!' });
t('st_adept_1', { title: 'Deckhand', name: 'Marlo', sprite: 'sailor', party: [['crabbit', 16], ['gullip', 16]], intro: 'All hands! We have a challenger!', lose: 'Man overboard!', after: "Cap'n Brann's Stormgull hits like a gale. Static Morphs'll ground it." });
t('st_adept_2', { title: 'Angler', name: 'Perch', sprite: 'fisher', party: [['zaplet', 16], ['jellume', 17]], intro: "Hooked you!", lose: "...I've been hooked.", after: 'Jellumes can poison you. Bring some Purge Herbs.' });
t('st_adept_3', { title: 'Deckhand', name: 'Bosun Tam', sprite: 'sailor', party: [['gullip', 17], ['crabbit', 17]], intro: "Last line before the Captain. Let's see your sea-legs!", lose: 'Solid sea-legs!', after: 'Go on. The Captain is waiting.' });
warden('brann', { title: 'Captain', name: 'Brann', sprite: 'brann', items: ['strong_tonic'], party: [['gullip', 16], ['crabbit', 17], ['jellume', 17], ['stormgull', 19]], intro: "Ha! The kid who cleared my pier. The sea tests everyone, {PLAYER}. Let's see if you float!", lose: "Ha-HA! You've got salt in your blood.", win: 'Sunk! Dry off and try again.' });

// ── Route 3 ───────────────────────────────────────────────────────────────
t('r3_hiker', { title: 'Hiker', name: 'Gunnar', sprite: 'hiker', party: [['pebbling', 18], ['tunnip', 18]], intro: "Rockfall ahead! Nothing for it but a battle.", lose: 'Rock bottom.', after: 'The Coldforge Mines cut straight through to Gearhollow.' });
t('r3_sailor', { title: 'Sailor', name: 'Rigg', sprite: 'sailor', party: [['gullip', 18], ['crabbit', 19]], intro: 'Ahoy! Ever battled on a beach? Sand gets EVERYWHERE.', lose: 'Sand in my... everything.', after: 'With a Skiff you can reach that little islet. Treasure, probably.' });
t('r3_twin', { title: 'Twin', name: 'Pip & Pat', sprite: 'twin', party: [['nibbit', 18], ['gnawbit', 19]], intro: 'We share everything! Including this beating we will give you!', lose: 'We share this loss, too.', after: "Nibbits evolve at level 18. We checked." });
t('r3_fisher', { title: 'Angler', name: 'Skip', sprite: 'fisher', party: [['jellume', 19], ['zaplet', 18], ['gullip', 18]], intro: 'Quiet! The fish can hear you. So can my Morphs.', lose: "Snapped my line.", after: 'The tide pools here are full of Crabbits.' });
t('r3_ace', { title: 'Ace Tamer', name: 'Juno', sprite: 'ace', skill: 2, reward: 40, party: [['voltquill', 19], ['knuckroo', 20]], intro: 'An Ace Tamer never backs down. Neither should you.', lose: 'You fight like an Ace already.', after: 'Voltquills evolve at 25. Their feathers crackle like a storm.' });

// ── Coldforge Mines ──────────────────────────────────────────────────────
t('cf_miner_1', { title: 'Miner', name: 'Dusty', sprite: 'miner', party: [['tunnip', 19], ['pebbling', 20]], intro: 'Oi! You in a hard hat? No? Then you get a battle!', lose: 'Should have worn MY hard hat.', after: 'Robed folk came down here a week ago and started digging where we never dig.' });
t('cf_miner_2', { title: 'Miner', name: 'Cole', sprite: 'miner', party: [['ferrite', 20], ['tunnip', 20]], intro: 'Down here the rock talks back. So do I!', lose: 'Tapped out.', after: 'They call it scale-iron. Warm to the touch. Hums. I don\'t like it.' });
t('cf_engineer', { title: 'Engineer', name: 'Pell', sprite: 'engineer', party: [['coilbit', 21], ['rivetle', 20]], intro: "I'm surveying the old workings. And you're blocking my survey.", lose: 'Survey says: I lost.', after: 'Take that disc over there. The Deepcall left it behind.' });
// Gullcliff Road: two acolytes trying to carry off a stranded Puddlet (the Puddlet rescue)
acolyte('r3_poacher_a', 'Sloane', [['oozelet', 16], ['gullip', 17]], { intro: "Back off! This Puddlet belongs to the Mother now. A Tide Morph for the Deepcall!", lose: "Ugh. Fine. It's only a puddle.", after: 'Keep the soggy thing. The Mother has bigger fish to fry.' });
acolyte('r3_poacher_b', 'Bram', [['crabbit', 16], ['echirp', 16], ['oozelet', 17]], { sprite: 'acolyte_b', intro: "You want the Puddlet? You'll have to get past me, kid!", lose: 'Sloane, run! This kid is serious!', after: 'We were only going to borrow it. For... ever.' });
acolyte('cf_acolyte_1', 'Durn', [['echirp', 20], ['oozelet', 20]], { intro: "Vesk said nobody gets past. So... nobody gets past!", lose: 'Vesk is going to be so annoyed.' });
acolyte('cf_acolyte_2', 'Lissa', [['crabbit', 21], ['pookit', 20]], { sprite: 'acolyte_b', intro: 'Do you hear it? The scale-iron sings. The Mother is dreaming!', lose: 'The song... stopped.' });
t('vesk1', { title: 'Deepcall Admin', name: 'Vesk', sprite: 'vesk', skill: 3, reward: 80, music: 'battle_boss', items: ['strong_tonic'], party: [['oozelet', 21], ['echirp', 22], ['vexgore', 24]], intro: "A child. They sent a CHILD to stop my dig? Fine. I'll bury you with the rest of the rock.", lose: 'Tch. Useless acolytes. Useless Morphs. Useless DAY.', win: 'Stay down.' });

// ── Gearhollow ───────────────────────────────────────────────────────────
acolyte('iw_acolyte_1', 'Brisk', [['oozelet', 21], ['echirp', 22]], { intro: 'The Ironworks is ours! We need the crane to lift the scale-iron!', lose: 'Crane... denied...' });
acolyte('iw_acolyte_2', 'Mira', [['jellume', 22], ['pookit', 22]], { sprite: 'acolyte_b', intro: "Warden Iskra won't hand over the forge. We'll take it.", lose: 'Maybe not today.' });
acolyte('iw_acolyte_3', 'Holt', [['vexgore', 23]], { intro: "You got past two of us? Impressive. Not impressive enough.", lose: "Okay, that was impressive enough." });
t('gh_adept_1', { title: 'Spark Adept', name: 'Volta', sprite: 'engineer', party: [['voltquill', 22], ['coilbit', 22]], intro: 'Charged and ready! Are you grounded?', lose: 'Short-circuited!', after: "Iskra's Coilossus has Iron armour. Brawl fists dent it." });
t('gh_adept_2', { title: 'Spark Adept', name: 'Ohm', sprite: 'scholar', party: [['coilbit', 23], ['ferrite', 23]], intro: 'Resistance is... measured in ohms. I am Ohm. Resist me!', lose: 'Zero resistance.', after: 'Stone Morphs are immune to Static attacks. Iskra hates that.' });
t('gh_adept_3', { title: 'Spark Adept', name: 'Ampere', sprite: 'engineer', party: [['voltquill', 23], ['fulmirex', 24]], intro: 'Last adept! Maximum current!', lose: 'Fuse blown!', after: 'Go get her. She has been waiting for a real challenge.' });
warden('iskra', { name: 'Iskra', sprite: 'iskra', items: ['strong_tonic', 'strong_tonic'], party: [['coilbit', 23], ['voltquill', 24], ['ferrite', 24], ['fulmirex', 26]], intro: "You saved my Ironworks. Now let's see if you can survive my Trial. I tuned everyone up this morning!", lose: 'Brilliant! Absolutely brilliant! I need to take notes.', win: 'Back to the drawing board — for you!' });

// ── Route 4 ───────────────────────────────────────────────────────────────
t('r4_mystic', { title: 'Mystic', name: 'Wynne', sprite: 'mystic', party: [['omenet', 26], ['mystaline', 26]], intro: 'The stones told me you would come this way. They also told me to battle you.', lose: 'The stones did not mention this part.', after: 'The circle of stones hums in the fog. So do the Seals.' });
t('r4_ranger', { title: 'Ranger', name: 'Hollis', sprite: 'ranger', party: [['lambkin', 26], ['trotterion', 27]], intro: 'Moorland rangers never lose their way. Or their battles!', lose: '...Lost my way, and the battle.', after: 'Hollowmere is just north. Follow the path — never the lights.' });
t('r4_scholar', { title: 'Scholar', name: 'Pemberton', sprite: 'scholar', party: [['omenet', 27], ['cairnite', 27]], intro: "I'm studying the stone circle. You're interrupting my study. Therefore: battle.", lose: 'Fascinating. Humiliating, but fascinating.', after: 'The inscriptions here predate the Wardens. They mention a "covenant".' });
t('r4_hiker', { title: 'Hiker', name: 'Tor', sprite: 'hiker', party: [['cragmaul', 27], ['brutusk', 26], ['pebbling', 26]], intro: "I've climbed every hill on this moor. Twice!", lose: 'Downhill from here.', after: "Frostspire's past Hollowmere and across the lake. You'll need a boat." });
t('r4_lady', { title: 'Lady', name: 'Cordelia', sprite: 'lady', skill: 2, reward: 60, party: [['mothlume', 27], ['pookit', 27]], intro: 'A walk on the moor, a battle with a stranger. How delightfully rustic.', lose: 'How delightfully... humbling.', after: 'Here, a lady always tips a worthy opponent. Well — the money was the tip.' });

// ── Hollowmere ───────────────────────────────────────────────────────────
t('hm_adept_1', { title: 'Veil Adept', name: 'Nox', sprite: 'mystic', party: [['pookit', 28], ['echirp', 28]], intro: 'In the dark, you hear more than you see. Listen...', lose: 'I heard that.', after: "Morrow's Vesperel strikes from the shadows. Don't let it build up." });
t('hm_adept_2', { title: 'Veil Adept', name: 'Umbrel', sprite: 'scholar', party: [['nyxen', 28], ['cairnite', 29]], intro: 'Every story has a shadow. I am yours.', lose: 'A short story, then.', after: 'Brawl moves strike Umbra Morphs hard.' });
t('hm_adept_3', { title: 'Veil Adept', name: 'Gloam', sprite: 'mystic', party: [['duskwing', 29], ['hollowisp', 29]], intro: "The Warden is listening to us right now. Make it a good story.", lose: 'A good story indeed.', after: 'Morrow will tell you a story whether you win or lose. Win.' });
warden('morrow', { name: 'Morrow', sprite: 'morrow', items: ['full_tonic'], party: [['pookit', 31], ['duskwing', 32], ['cairnite', 32], ['vesperel', 34]], intro: "Every Trial is a story, {PLAYER}. Mine is a ghost story. Let's see how yours ends.", lose: '...And the hero walked out of the fog. A good ending.', win: 'Not every story ends well. Try again.' });
t('maren1', { title: 'Deepcall Admin', name: 'Maren', sprite: 'maren', skill: 3, reward: 80, music: 'battle_boss', items: ['full_tonic'], party: [['omenet', 30], ['jellume', 30], ['strixage', 32]], intro: "Please don't make this harder than it has to be. I would rather talk. But if you insist...", lose: "You fight for what you believe. So do we. Remember that.", win: "I'm sorry. Truly." });

// ── Route 5 ───────────────────────────────────────────────────────────────
t('r5_fisher', { title: 'Angler', name: 'Bass', sprite: 'fisher', party: [['jellume', 30], ['croakmire', 30], ['zaplet', 30]], intro: 'An island all to myself — until YOU paddled up.', lose: 'Back to my island solitude.', after: 'Glasslake is so clear you can see the old road under the water.' });
t('r5_sailor', { title: 'Sailor', name: 'Ness', sprite: 'sailor', party: [['stormgull', 31], ['pincerock', 30]], intro: 'Ahoy, landlubber! Or should I say... lakelubber?', lose: 'Nobody says lakelubber. My bad.', after: 'The fog thins as you head north. Colder, though.' });
t('r5_skier', { title: 'Skier', name: 'Freya', sprite: 'skier', party: [['frostkit', 31], ['flurrit', 31]], intro: 'First snow of the season! Let me show you how we battle up north!', lose: 'Wiped out!', after: 'Frostspire is right up the path. Warm your hands at the Haven.' });
t('r5_mystic', { title: 'Mystic', name: 'Lune', sprite: 'mystic', party: [['strixage', 31]], intro: 'I rowed out here to meditate. You rowed out here to battle. Very well.', lose: 'Inner peace... disturbed.', after: 'Leave me to my islet. And take the pearl, if you like.' });
t('r5_ace', { title: 'Ace Tamer', name: 'Kestrel', sprite: 'ace_b', skill: 2, reward: 45, party: [['skyveer', 31], ['pugilus', 31], ['medusheen', 32]], intro: 'Only strong Tamers make it this far. Are you one?', lose: 'You are.', after: 'Hale in Frostspire is tougher than the mountain she climbs.' });

// ── Frostspire ───────────────────────────────────────────────────────────
t('fs_adept_1', { title: 'Rime Adept', name: 'Sigrid', sprite: 'skier', party: [['chillcub', 33], ['lambkin', 33]], intro: 'Keep your footing, challenger. The floor is ice!', lose: 'Slipped up!', after: "Hale's Glaciursa hits like an avalanche." });
t('fs_adept_2', { title: 'Rime Adept', name: 'Bjorn', sprite: 'hiker', party: [['rammoth', 34]], intro: 'ONE Morph. ONE hit. That is all I need!', lose: 'Needed two hits.', after: 'Fire melts ice. Obviously. Stone and Iron shatter it too.' });
t('fs_adept_3', { title: 'Rime Adept', name: 'Astrid', sprite: 'skier', party: [['glacivix', 34], ['chillcub', 34]], intro: 'Last stop before the summit!', lose: 'Summit reached. By you.', after: 'The Warden is waiting at the top. Go.' });
warden('hale', { name: 'Hale', sprite: 'hale', items: ['full_tonic', 'full_tonic'], party: [['chillcub', 34], ['flurrit', 35], ['rammoth', 35], ['glaciursa', 37]], intro: "You crossed Glasslake to get here? Good. The mountain respects effort. So do I. Now — climb!", lose: 'Ha! Summited! The Rime Sigil is yours.', win: 'The mountain wins today. It usually does.' });

// ── Route 6 ───────────────────────────────────────────────────────────────
t('r6_skier_1', { title: 'Skier', name: 'Lars', sprite: 'skier', party: [['glaciursa', 35], ['flurrit', 35]], intro: 'Downhill all the way to Riftgate! Race you — well, battle you!', lose: 'Crashed into a snowbank.', after: 'The snow stops where the ash starts. Nothing grows near the Riven.' });
t('r6_skier_2', { title: 'Skier', name: 'Elin', sprite: 'skier', party: [['rammoth', 36], ['chillcub', 35]], intro: 'Watch out — ledge!', lose: 'Watch out — loss!', after: 'You can hop down those ledges. Climbing back up is another matter.' });
t('r6_hiker', { title: 'Hiker', name: 'Ulf', sprite: 'hiker', party: [['borebeast', 36], ['cragmaul', 36]], intro: "The pass is steep and I am steeper!", lose: 'Levelled.', after: 'There were robed folk marching down this pass. Dozens of them.' });
acolyte('r6_acolyte', 'Corvin', [['vexgore', 36], ['duskwing', 37]], { intro: "The Hierophant said a Tamer with Sigils would come. Are you... the key?", lose: 'You ARE the key... I must tell Oriel!' });
t('r6_ace', { title: 'Ace Tamer', name: 'Sol', sprite: 'ace', skill: 2, reward: 45, party: [['arcfowl', 37], ['mantiscythe', 37], ['wyverant', 36]], intro: 'Five Sigils? You must be heading for the Wyrm Trial. Prove you deserve it!', lose: 'You deserve it.', after: "Seren's Riftwyrm is the strongest Morph I've ever seen. Frost is its weakness." });

// ── Riftgate ─────────────────────────────────────────────────────────────
t('rg_adept_1', { title: 'Wyrm Adept', name: 'Draco', sprite: 'ace', party: [['wyrmkin', 38], ['cragmaul', 38]], intro: 'The Wyrm Trial is the last Trial. It is also the hardest.', lose: 'Hardest... for me.', after: 'Seren has never lost two Trials in a row. You might be the first.' });
t('rg_adept_2', { title: 'Wyrm Adept', name: 'Ember', sprite: 'ace_b', party: [['magmaw', 39], ['wyverant', 39]], intro: "Dragons don't flinch. Do you?", lose: 'I flinched.', after: 'Drake moves hit Drake Morphs super hard. Use that.' });
t('rg_adept_3', { title: 'Wyrm Guard', name: 'Aldric', sprite: 'guard', party: [['ferroclad', 39], ['wyrmguard', 40]], intro: 'I guard the Warden. You shall not pass!', lose: 'You shall pass.', after: 'The Warden waits.' });
warden('seren', { name: 'Seren', sprite: 'seren', items: ['full_tonic', 'full_tonic'], party: [['wyrmguard', 40], ['flurrit', 39], ['arcfowl', 40], ['strixage', 39], ['riftwyrm', 42]], intro: "Five Sigils. You have walked the whole Reach to stand here. I will not go easy on you, {PLAYER}. Stand at the edge — and do not flinch.", lose: 'You did not flinch. Neither will I, when the time comes.', win: 'You flinched.' });

// ── Sunken Chapel ────────────────────────────────────────────────────────
acolyte('sc_acolyte_1', 'Selka', [['medusheen', 40], ['vexgore', 40]], { intro: 'The Hierophant is below. You will not reach them!', lose: 'Go, then. It is already too late.' });
acolyte('sc_acolyte_2', 'Brine', [['stormgull', 41], ['pincerock', 41]], { sprite: 'acolyte_b', intro: "The Mother stirs. Can you feel the floor shaking?", lose: 'The floor is still shaking...' });
acolyte('sc_acolyte_3', 'Moll', [['duskwing', 41], ['jellume', 40]], { intro: 'Your friend chose us. Why won\'t you?', lose: 'Maybe... your friend chose wrong.' });
acolyte('sc_acolyte_4', 'Drift', [['noctheart', 42]], { sprite: 'acolyte_b', intro: 'For the tide! For the Mother!', lose: 'For... the Mother...' });
t('vesk2', { title: 'Deepcall Admin', name: 'Vesk', sprite: 'vesk', skill: 3, reward: 80, music: 'battle_boss', items: ['full_tonic'], party: [['duskwing', 42], ['pincerock', 42], ['borebeast', 42], ['vexgore', 44]], intro: "YOU. The brat from the mines. The Hierophant says I'm not to hurt you. The Hierophant isn't here.", lose: "...Go on, then. Go see the Mother. You'll wish you hadn't.", win: 'Stay down this time.' });
t('maren2', { title: 'Deepcall Admin', name: 'Maren', sprite: 'maren', skill: 3, reward: 80, music: 'battle_boss', items: ['full_tonic', 'full_tonic'], party: [['augurine', 43], ['medusheen', 43], ['stormgull', 43], ['strixage', 45]], intro: 'Wren trusted me. I told them the truth — as I understood it. Maybe I was wrong. Show me.', lose: '...I was wrong. Take Wren. Go.', win: "I'm sorry, {PLAYER}." });

// ── Abyssal Rift & the Cradle ────────────────────────────────────────────
acolyte('ar_acolyte_1', 'Undine', [['medusheen', 43], ['duskwing', 43]], { intro: 'The Hierophant is waking her NOW! You are too late!', lose: 'Too late... for me.' });
acolyte('ar_acolyte_2', 'Keel', [['pincerock', 44], ['vexgore', 44]], { sprite: 'acolyte_b', intro: "Turn back! The Mother's breath will drown you!", lose: 'Drowned... in defeat.' });
acolyte('ar_acolyte_3', 'Fathom', [['noctheart', 44], ['stormgull', 44]], { intro: 'We have waited a thousand years for this night!', lose: 'Wait a little longer, I suppose.' });
t('ar_ace', { title: 'Deepcall Warden', name: 'Tidewright', sprite: 'ace_b', skill: 3, reward: 70, music: 'battle_deepcall', party: [['riftwyrm', 45], ['maelstrand', 44]], intro: "I was a Warden once, like Seren. Then I heard the Mother sing. You'll hear her too.", lose: '...She is louder now. Go. Go and see.', after: 'Go.' });
t('oriel', { title: 'Hierophant', name: 'Oriel', sprite: 'oriel', skill: 3, reward: 150, music: 'battle_oriel', bg: 'rift', items: ['full_tonic'], party: [['vexgore', 44], ['duskwing', 44], ['medusheen', 45], ['augurine', 45], ['noctheart', 47]], intro: "Thank you, {PLAYER}. Six Sigils, six Seals, one Cradle — opened. You did everything I needed. Now let me show you what you've done.", lose: 'It does not matter. She is awake. Listen...', win: 'Rest now. The tide will carry you.' });
