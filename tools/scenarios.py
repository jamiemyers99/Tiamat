async def world(t, port):
    await t.p.goto(f'http://localhost:{port}/?map=rootmere&x=16&y=8&debug')
    await t.wait(2500)
    await t.shot('rootmere')
    await t.keys(['ArrowDown'] * 4, hold=400, after=50)
    await t.wait(300)
    await t.shot('walked')
    await t.js("window.__tiamat.G.state.clock = 22*60")
    await t.wait(400)
    await t.shot('night')

async def battle(t, port):
    await t.p.goto(f'http://localhost:{port}/?map=route1&x=16&y=10&debug')
    await t.wait(2500)
    await t.js("""(() => { const T = window.__tiamat; T.G.state.party = [T.createMon('cindlet', 6), T.createMon('puddlet', 5)]; T.G.state.bag.capsule = 5; T.G.state.bag.tonic = 3; })()""")
    await t.js("void window.__tiamat.game.scene.getScene('World').S.wild('beakling', 4)")
    await t.wait(2600)
    await t.shot('battle_intro')
    for i in range(6):
        await t.key('z', 60, 400)
    await t.shot('battle_menu')
    await t.key('z', 60, 300)
    await t.shot('moves')
    await t.key('z', 60, 300)
    for i in range(10):
        await t.key('z', 60, 450)
        if i == 2: await t.shot('attack')
    await t.shot('after_turn')


# ── full story smoke test: runs every major script with an auto-confirm "masher" ──
AUTO = """(() => {
  const I = window.__tiamat.input;
  if (window.__auto) { clearInterval(window.__auto); }
  let on = false;
  const W = window.__tiamat.game.scene.getScene('World');
  window.__auto = setInterval(() => {
    // only press while a script, battle or menu is running — never trigger new things in the idle world
    const idle = W.busy === 0 && I.top() === 'world';
    on = !on && !idle;
    if (on) { I.keysDown.add('confirm'); } else { I.keysDown.delete('confirm'); }
  }, 70);
})()"""
W = "window.__tiamat.game.scene.getScene('World')"


async def wait_for(t, cond, timeout=90000, label=''):
    step = 250
    for _ in range(timeout // step):
        if await t.js(f"(() => {{ try {{ return !!({cond}); }} catch (e) {{ return false; }} }})()"):
            return True
        await t.wait(step)
    print(f'TIMEOUT waiting for {label or cond}')
    await t.shot('timeout_' + (label or 'x').replace(' ', '_')[:20])
    return False


async def idle(t, timeout=90000, label=''):
    # world not busy, no battle, no menu, top of input stack is the world
    return await wait_for(t, f"{W}.busy === 0 && window.__tiamat.input.top() === 'world' && !window.__tiamat.game.scene.isActive('Battle')", timeout, label)


async def goto(t, m, x, y, face='down'):
    await t.js(f"{W}.transition('{m}', {x}, {y}, '{face}')")
    await t.wait(700)
    await idle(t, 30000, f'arrive {m}')


async def run_script(t, sid, label=None, timeout=120000):
    await t.js("window.__tiamat.G.state.party.forEach(m => { window.__tiamat.healMon(m); m.moves.forEach(mv => { mv.pp = 999; mv.max = 999; }); })")
    await t.js(f"void {W}.run('{sid}')")
    await t.wait(400)
    await idle(t, timeout, label or sid)


async def story(t, port):
    await t.p.goto(f'http://localhost:{port}/?map=home_2f&x=5&y=4&debug')
    await t.wait(3000)
    await t.js("(() => { const G = window.__tiamat.G; G.settings.textSpeed = 'instant'; G.settings.battleAnims = false; })()")
    await t.js(AUTO)
    # the Trial adepts are covered by the trialgate scenario; here we go straight to each Warden
    await t.js("(() => { const d = window.__tiamat.G.state.defeated; for (const p of ['bw', 'st', 'gh', 'hm', 'fs', 'rg']) { for (const i of [1, 2, 3]) { d[`${p}_adept_${i}`] = true; } } })()")
    await idle(t, 20000, 'wake')
    flags = lambda: t.js("Object.keys(window.__tiamat.G.state.flags).join(',')")
    # Act I
    await goto(t, 'marsh_lab', 6, 8, 'up')
    await t.shot('lab')
    await run_script(t, 'lab.starters')
    print('party after lab:', await t.js("window.__tiamat.G.state.party.map(m => m.species + ':' + m.level).join(',')"))
    print('bag:', await t.js("JSON.stringify(window.__tiamat.G.state.bag)"))
    await goto(t, 'rootmere', 24, 7)
    await t.shot('rootmere_after_mum')
    print('boots:', await t.js("window.__tiamat.G.state.bag.trail_boots"))
    await t.js("""(() => { const T = window.__tiamat; T.G.state.party = [T.createMon('pyromane', 74), T.createMon('glaciursa', 75, { moves: ['icicle_jab', 'hail_volley', 'power_kick', 'all_out_slam'] }), T.createMon('maelstrand', 74, { moves: ['rime_ray', 'hydro_burst', 'icicle_jab', 'undertow'] }), T.createMon('mosswarden', 72, { moves: ['quake_stomp', 'timber_crash', 'bloom_blast', 'heal_bud'] })]; })()""")
    await goto(t, 'brindlewood_trial', 6, 16, 'up')
    await run_script(t, 'brindlewood_trial.warden')
    await goto(t, 'brindlewood_house', 5, 7, 'up')
    await run_script(t, 'brindlewood.aldous')
    # Act II
    await t.js("(() => { const d = window.__tiamat.G.state.defeated; d.tw_acolyte_1 = d.tw_acolyte_2 = true; })()")
    await goto(t, 'thornwild', 30, 34)
    await t.js(f"{W}.player.warp(30, 35, 'down')")
    await run_script(t, 'thornwild.wren')
    await goto(t, 'saltreach', 20, 26, 'down')
    await t.js("(() => { const d = window.__tiamat.G.state.defeated; d.st_acolyte_1 = d.st_acolyte_2 = true; })()")
    await run_script(t, 'saltreach.brann_docks')
    await goto(t, 'saltreach_trial', 6, 16, 'up')
    await run_script(t, 'saltreach_trial.warden')
    await goto(t, 'coldforge_mines', 39, 21, 'up')
    await t.shot('mines')
    await run_script(t, 'mines.vesk')
    await t.js("(() => { const d = window.__tiamat.G.state.defeated; d.iw_acolyte_1 = d.iw_acolyte_2 = d.iw_acolyte_3 = true; })()")
    await goto(t, 'gearhollow_ironworks', 10, 4, 'up')
    await run_script(t, 'ironworks.iskra')
    await goto(t, 'gearhollow_trial', 6, 16, 'up')
    await run_script(t, 'gearhollow_trial.warden')
    await goto(t, 'gearhollow', 27, 25, 'down')
    await run_script(t, 'gearhollow.wren')
    # Act III
    await goto(t, 'hollowmere_trial', 6, 16, 'up')
    await run_script(t, 'hollowmere_trial.warden')
    await goto(t, 'hollowmere', 14, 16, 'left')
    await run_script(t, 'hollowmere.shore')
    await t.shot('hollowmere')
    # Act IV
    await goto(t, 'frostspire_trial', 6, 16, 'up')
    await run_script(t, 'frostspire_trial.warden')
    await goto(t, 'riftgate_trial', 6, 16, 'up')
    await run_script(t, 'riftgate_trial.warden')
    await goto(t, 'riftgate', 23, 10, 'down')
    await t.js("window.__tiamat.G.state.party.forEach(window.__tiamat.healMon)")
    await t.js(f"void {W}.run('riftgate.oriel')")
    await t.wait(2500)
    await t.shot('oriel_reveal')
    await idle(t, 60000, 'oriel scene')
    await goto(t, 'sunken_chapel', 11, 9, 'up')
    await run_script(t, 'chapel.maren')
    await goto(t, 'sunken_chapel', 10, 5, 'up')
    await run_script(t, 'chapel.wren')
    await goto(t, 'cradle', 9, 10, 'up')
    await t.js("window.__tiamat.G.state.party.forEach(window.__tiamat.healMon)")
    await t.js(f"void {W}.run('cradle.oriel')")
    await wait_for(t, "window.__tiamat.G.state.flags.oriel_beaten", 120000, 'oriel beaten')
    await t.wait(3500)
    await t.shot('tiamat_rises')
    await wait_for(t, "window.__tiamat.G.state.player.map === 'spire_crown'", 180000, 'crown')
    await t.js("window.__tiamat.G.state.party.forEach(m => { window.__tiamat.healMon(m); m.moves.forEach(mv => { mv.pp = 999; mv.max = 999; }); })")
    await wait_for(t, "window.__tiamat.G.state.flags.game_clear", 240000, 'game clear')
    await t.wait(2000)
    await t.shot('credits')
    await wait_for(t, "window.__tiamat.G.state.player.map === 'home_2f'", 120000, 'home again')
    await idle(t, 60000, 'epilogue')
    await t.shot('home')
    print('sigils:', await t.js("window.__tiamat.G.state.sigils.join(',')"))
    print('flags:', await flags())
    print('key items:', await t.js("Object.keys(window.__tiamat.G.state.bag).join(',')"))


async def tour(t, port):
    await t.p.goto(f'http://localhost:{port}/')
    await t.wait(3500)
    await t.shot('title')
    await t.p.goto(f'http://localhost:{port}/?map=brindlewood&x=19&y=20&debug')
    await t.wait(3000)
    await t.js("window.__tiamat.G.settings.textSpeed = 'instant'")
    for (m, x, y, clock) in [('brindlewood', 19, 18, 10), ('saltreach', 21, 14, 18), ('gearhollow', 20, 16, 13), ('frostspire', 18, 18, 11),
                             ('riftgate', 20, 19, 21), ('route6', 30, 20, 12), ('thornwild', 27, 30, 15), ('abyssal_rift', 20, 8, 12), ('route4', 16, 30, 17)]:
        await t.js(f"window.__tiamat.G.state.clock = {clock}*60")
        await t.js(f"{W}.transition('{m}', {x}, {y}, 'down')")
        await t.wait(2600)
        await t.shot(m)
    # Reach map + legendary battle
    await t.js("(() => { const T = window.__tiamat; T.G.state.bag.reach_map = 1; T.G.state.bag.wing_whistle = 1; T.G.state.flags.visited_brindlewood = true; T.G.state.party = [T.createMon('mosswarden', 55)]; })()")
    await t.js(f"{W}.openMenu()")
    await t.wait(800)
    await t.shot('menu')
    await t.key('x'); await t.wait(500)
    await t.js(f"void {W}.S.wild('tiamat', 50, {{ noRun: true, music: 'battle_legend', bg: 'rift' }})")
    await t.wait(3500)
    await t.shot('tiamat_battle')


async def finale(t, port):
    await t.p.goto(f'http://localhost:{port}/?map=cradle&x=9&y=12&debug')
    await t.wait(3000)
    await t.js("""(() => { const T = window.__tiamat; const G = T.G; G.settings.textSpeed = 'instant'; G.settings.battleAnims = false;
      for (const f of ['got_starter','sigil_moss','sigil_tide','sigil_spark','sigil_veil','sigil_rime','sigil_wyrm','oriel_reveal','wren_freed','maren2_done','vesk2_done']) G.state.flags[f] = true;
      G.state.sigils = ['moss','tide','spark','veil','rime','wyrm']; G.state.vars.starter = 'cindlet';
      G.state.party = [T.createMon('glaciursa', 75, { moves: ['icicle_jab', 'hail_volley', 'power_kick', 'all_out_slam'] }),
                       T.createMon('maelstrand', 74, { moves: ['rime_ray', 'hydro_burst', 'icicle_jab', 'undertow'] }),
                       T.createMon('pyromane', 74)];
      G.state.party.forEach(m => m.moves.forEach(mv => { mv.pp = 999; mv.max = 999; }));
      G.state.bag.covenant_capsule = 1; })()""")
    await t.js(AUTO)
    await t.js(f"void {W}.run('cradle.oriel')")
    await wait_for(t, "window.__tiamat.G.state.flags.oriel_beaten", 120000, 'oriel beaten')
    await t.wait(2600)
    await t.shot('tiamat_rises')
    await wait_for(t, "window.__tiamat.game.scene.isActive('Battle') && window.__tiamat.game.scene.getScene('Battle').battle && window.__tiamat.game.scene.getScene('Battle').battle.e.mon.species === 'tiamat'", 60000, 'tiamat battle')
    await t.wait(1500)
    await t.shot('tiamat_battle')
    await wait_for(t, "window.__tiamat.G.state.player.map === 'spire_crown'", 180000, 'crown')
    await t.wait(1500)
    await t.shot('crown')
    await wait_for(t, "window.__tiamat.G.state.flags.game_clear", 240000, 'game clear')
    await t.wait(3000)
    await t.shot('credits')
    await wait_for(t, "window.__tiamat.G.state.player.map === 'home_2f'", 180000, 'home again')
    await idle(t, 60000, 'epilogue')
    await t.shot('home')
    print('flags:', await t.js("Object.keys(window.__tiamat.G.state.flags).join(',')"))


async def fly(t, port):
    await t.p.goto(f'http://localhost:{port}/?map=gearhollow&x=12&y=14&debug')
    await t.wait(3000)
    await t.js("""(() => { const T = window.__tiamat; const G = T.G; G.settings.textSpeed = 'instant';
      G.state.bag.reach_map = 1; G.state.bag.wing_whistle = 1; G.state.flags.visited_brindlewood = true;
      G.state.party = [T.createMon('skyveer', 30)]; })()""")
    await t.js(f"{W}.openMenu()")
    await t.wait(700)
    # main menu: Team, Bag, Map ... → move to Map
    items = await t.js("[...(window.__tiamat.game.scene.getScene('Menu').children.list)].length")
    for _ in range(2): await t.key('ArrowDown')
    await t.key('z'); await t.wait(600)
    await t.shot('reachmap')
    # cursor starts on the current location (gearhollow); step back until Brindlewood
    for _ in range(6):
        txt = await t.js("window.__tiamat.game.scene.getScene('Menu').children.list.map(c => c.list ? c.list.map(x => x.text || '').join('|') : (c.text || '')).join('|')")
        if 'Brindlewood' in txt and '[Confirm: fly]' in txt: break
        await t.key('ArrowLeft'); await t.wait(150)
    await t.shot('reachmap_brindlewood')
    await t.key('z'); await t.wait(500)
    await t.key('z'); await t.wait(1800)
    print('after fly:', await t.js("window.__tiamat.G.state.player.map + ' ' + window.__tiamat.G.state.player.x + ',' + window.__tiamat.G.state.player.y"))
    print('input top:', await t.js("window.__tiamat.input.top()"), 'menu active:', await t.js("window.__tiamat.game.scene.isActive('Menu')"))
    await t.shot('landed')
    # open and close the menu again — no ghost listeners should react
    await t.js(f"{W}.openMenu()")
    await t.wait(600)
    await t.key('x'); await t.wait(600)
    print('after reopen/close top:', await t.js("window.__tiamat.input.top()"), 'menu active:', await t.js("window.__tiamat.game.scene.isActive('Menu')"))


async def newgame(t, port):
    await t.p.goto(f'http://localhost:{port}/')
    await t.wait(3000)
    await t.key('z'); await t.wait(800)
    await t.shot('title_menu')
    await t.key('z'); await t.wait(1500)          # New Game
    for i in range(40):
        top = await t.js("window.__tiamat.input.top()")
        if await t.js("!!(window.__tiamat.input.textListener)"):
            break
        await t.key('z', 50, 180)
    await t.shot('name_entry')
    for ch in 'Myro':
        await t.p.keyboard.press(ch)
        await t.wait(80)
    await t.p.keyboard.press('Enter')
    for i in range(40):
        if await t.js("window.__tiamat.game.scene.isActive('World')"):
            break
        await t.key('z', 50, 200)
    await t.wait(1500)
    for i in range(8):
        await t.key('z', 50, 200)
    await t.shot('bedroom')
    print('name:', await t.js("window.__tiamat.G.state.player.name"), 'map:', await t.js("window.__tiamat.G.state.player.map"))


async def controls(t, port):
    await t.p.goto(f'http://localhost:{port}/?map=rootmere&x=16&y=12&debug')
    await t.wait(3000)
    await t.js(f"{W}.openMenu()")
    await t.wait(700)
    # find "Controls" in the pause menu
    labels = await t.js("window.__tiamat.game.scene.getScene('Menu').children.list.flatMap(c => c.list ? c.list : [c]).map(x => x.text || '').filter(Boolean).join('|')")
    print('menu:', labels)
    order = [x.strip() for x in labels.split('|') if x.strip() in ('Team', 'Bag', 'Index', 'Map', 'Rowan', 'Save', 'Controls', 'Options', 'Close')]
    for _ in range(order.index('Controls')):
        await t.key('ArrowDown')
    await t.key('z'); await t.wait(600)
    await t.shot('controls')
    # rebind "Move up" key 1 to I
    await t.key('z'); await t.wait(300)
    await t.p.keyboard.press('i'); await t.wait(300)
    # "Talk / confirm" key 1 to K
    for _ in range(4):
        await t.key('ArrowDown')
    await t.key('z'); await t.wait(300)
    await t.p.keyboard.press('k'); await t.wait(300)
    await t.shot('controls_changed')
    print('bindings:', await t.js("JSON.stringify(window.__tiamat.input.bindings)"))
    await t.key('x'); await t.wait(400)
    await t.key('x'); await t.wait(700)
    print('top:', await t.js("window.__tiamat.input.top()"))
    y0 = await t.js(f"{W}.player.ty")
    await t.key('i', 350, 400)
    await t.key('i', 350, 400)
    y1 = await t.js(f"{W}.player.ty")
    print('moved up with I:', y0, '->', y1)
    print('saved:', await t.js("localStorage.getItem('tiamat.settings')"))
    # reload: bindings survive
    await t.p.reload(); await t.wait(3000)
    print('after reload:', await t.js("JSON.stringify(window.__tiamat.input.bindings.up) + ' ' + JSON.stringify(window.__tiamat.input.bindings.confirm)"))


async def difficulty(t, port):
    await t.p.goto(f'http://localhost:{port}/?map=route1&x=16&y=44&debug')
    await t.wait(3000)
    await t.js("(() => { const T = window.__tiamat; T.G.settings.textSpeed = 'instant'; T.G.state.party = [T.createMon('cindlet', 6)]; })()")
    await t.js(f"void {W}.S.wild('nibbit', 3)")
    await t.wait(3000)
    print('route1 wild ivs:', await t.js("JSON.stringify(window.__tiamat.game.scene.getScene('Battle').battle.e.mon.ivs)"), 'wild AI:', await t.js("window.__tiamat.game.scene.getScene('Battle').battle.opts.wildSkill"))
    await t.shot('route1_wild')
    await t.js("window.__tiamat.game.scene.getScene('Battle').cfg.onEnd({ outcome: 'run' })")
    await t.wait(1200)
    await t.js(f"void {W}.S.battle('r1_ollie')")
    await t.wait(3000)
    B = "window.__tiamat.game.scene.getScene('Battle')"
    print('route1 tamer ivs:', await t.js(f"JSON.stringify({B}.battle.e.mon.ivs)"), 'skill:', await t.js(f"{B}.battle.trainer.skill"))
    await t.js(f"{B}.cfg.onEnd({{ outcome: 'run' }})")
    await t.wait(1200)
    await t.js(f"{W}.transition('riftgate_trial', 6, 16, 'up')")
    await t.wait(1500)
    await t.js(f"void {W}.S.battle('seren')")
    await t.wait(3000)
    print('riftgate warden ivs:', await t.js(f"JSON.stringify({B}.battle.e.mon.ivs)"), 'skill:', await t.js(f"{B}.battle.trainer.skill"))


# ── an older save (before male/female Index forms) loads, and the caught mark follows the form ──
async def forms(t, port):
    await t.p.goto(f'http://localhost:{port}/')
    await t.wait(2500)
    await t.js("""(() => { const T = window.__tiamat; const s = T.state.newState();
      s.player.name = 'Jamie'; s.player.map = 'route1'; s.player.x = 16; s.player.y = 10;
      const m = T.createMon('beakling', 8, { sex: 'm' }); delete m.nature;
      s.party = [T.createMon('cindlet', 12), m];
      s.index = { seen: ['beakling', 'cindlet'], caught: ['beakling', 'cindlet'] };
      s.flags.got_index = true; s.bag.capsule = 5;
      delete s.sexTally; delete s.xpShareOn; delete s.starterMoves2; delete s.player.gender;
      localStorage.setItem(T.state.slotKey(0), JSON.stringify(s)); })()""")
    await t.p.reload()
    await t.wait(2500)
    ok = await t.js("window.__tiamat.state.loadGame(0)")
    ix = await t.js("JSON.stringify(window.__tiamat.G.state.index)")
    print('loaded old save:', ok, ix)
    await t.js("window.__tiamat.game.scene.getScene('Title').scene.start('World')")
    await t.wait(2500)
    print('map:', await t.js("window.__tiamat.G.state.player.map"), 'party:', await t.js("window.__tiamat.G.state.party.map(m => m.species + ':' + m.sex + ':' + m.nature).join(' ')"))
    for sex in ['m', 'f']:
        await t.js(f"void {W}.S.wild('beakling', 4, {{ sex: '{sex}' }})")
        await t.wait(3200)
        vis = await t.js("(() => { const B = window.__tiamat.game.scene.getScene('Battle'); return B.battle.e.mon.sex + ' mark=' + B.eCaught.visible; })()")
        print('wild beakling', vis)
        await t.shot(f'battle_{sex}')
        await t.js("window.__tiamat.game.scene.getScene('Battle').battle.outcome = 'fled'")
        for _ in range(3): await t.key('Escape', 60, 150)
        await t.js("(() => { const B = window.__tiamat.game.scene.getScene('Battle'); if (B.scene.isActive()) { B.cfg.onEnd({ outcome: 'fled' }); B.scene.stop(); } })()")
        await t.wait(1200)
    await t.js("(() => { const W = window.__tiamat.game.scene.getScene('World'); W.scene.launch('Menu', { mode: 'index', species: 'beakling', onClose: () => {} }); W.scene.bringToTop('Menu'); })()")
    await t.wait(1500)
    await t.shot('index')
    await t.key('z', 60, 400)
    await t.shot('index_female')


# ── starter rescue quests + tall grass (rustle and wind) ──
async def rescue(t, port):
    await t.p.goto(f'http://localhost:{port}/?map=route1&x=8&y=26&debug')
    await t.wait(3000)
    await t.js("""(() => { const T = window.__tiamat, G = T.G; G.settings.textSpeed = 'instant'; G.settings.battleAnims = false;
      G.state.vars.starter = 'cindlet'; G.state.flags.got_starter = true; G.state.flags.got_index = true;
      G.state.party = [T.createMon('cindreaver', 34)]; G.state.bag.tonic = 2; G.state.bag.brush_hook = 1; G.state.bag.capsule = 0; })()""")
    # grass: step north into the patch and catch the rustle mid-step
    await t.shot('grass_still')
    await t.p.keyboard.down('ArrowUp'); await t.wait(110); await t.shot('grass_rustle'); await t.wait(200); await t.p.keyboard.up('ArrowUp')
    await t.wait(900); await t.shot('grass_standing')
    await t.js(AUTO)
    # Spriglet (Thornwild)
    await goto(t, 'thornwild', 6, 26, 'left')
    print('spriglet visible:', await t.js(f"{W}.npcById('tw_spriglet').active"), 'brambles:', await t.js(f"{W}.itemsOnMap.filter(i => i.bramble).length"))
    await t.shot('spriglet_brambles')
    await run_script(t, 'rescue.spriglet')
    print('spriglet:', await t.js("JSON.stringify(window.__tiamat.G.state.party.map(m => [m.species, m.level, m.sex]))"), 'flag', await t.js("!!window.__tiamat.G.state.flags.rescued_spriglet"), 'npc', await t.js(f"{W}.npcById('tw_spriglet').active"), 'tonics', await t.js("window.__tiamat.G.state.bag.tonic"))
    # Puddlet (Route 3)
    await goto(t, 'route3', 8, 17, 'down')
    print('puddlet visible:', await t.js(f"{W}.npcById('r3_puddlet').active"))
    await t.shot('puddlet_acolytes')
    await t.js(f"void {W}.S.battle('r3_poacher_a')"); await t.wait(500); await idle(t, 60000, 'poacher a')
    await t.js(f"void {W}.S.battle('r3_poacher_b')"); await t.wait(500); await idle(t, 60000, 'poacher b')
    await run_script(t, 'rescue.puddlet')
    print('puddlet:', await t.js("JSON.stringify(window.__tiamat.G.state.party.map(m => [m.species, m.level, m.sex]))"), await t.js("!!window.__tiamat.G.state.flags.rescued_puddlet"))
    # Cindlet (Coldforge Mines + Gearhollow smith), as if the starter had been Spriglet
    await t.js("window.__tiamat.G.state.vars.starter = 'spriglet'")
    await goto(t, 'coldforge_mines', 2, 13, 'down')
    print('cindlet visible:', await t.js(f"{W}.npcById('cf_cindlet').active"))
    await t.shot('cindlet_mines')
    await run_script(t, 'rescue.cindlet')
    await goto(t, 'gearhollow', 38, 13, 'up')
    await run_script(t, 'gearhollow.smith')
    print('ember:', await t.js("window.__tiamat.G.state.bag.forge_ember"))
    await goto(t, 'coldforge_mines', 2, 13, 'down')
    await run_script(t, 'rescue.cindlet')
    print('cindlet:', await t.js("JSON.stringify(window.__tiamat.G.state.party.map(m => [m.species, m.level, m.sex]))"), await t.js("!!window.__tiamat.G.state.flags.rescued_cindlet"))
    await t.js("clearInterval(window.__auto); window.__tiamat.input.keysDown.delete('confirm')")
    await t.js(f"(() => {{ const w = {W}; w.scene.launch('Menu', {{ mode: 'index', species: 'spriglet', onClose: () => {{}} }}); w.scene.bringToTop('Menu'); }})()")
    await t.wait(1200)
    await t.shot('index_spriglet')


async def rustle(t, port):
    await t.p.goto(f'http://localhost:{port}/?map=route1&x=7&y=23&debug')
    await t.wait(3000)
    await wait_for(t, f"{W}.player", 20000, 'player')
    await t.js(f"{W}.player.setFace('up'); window.__tiamat.G.state.player.face = 'up'")
    await t.wait(200)
    await t.p.keyboard.down('ArrowUp'); await t.wait(70); await t.shot('rustle_a')
    print('rustle:', await t.js(f"{W}.children.list.filter(o => o.frame && String(o.frame.name).startsWith('grass_rustle')).map(o => o.frame.name).join(',')"))
    print('player on screen:', await t.js(f"(() => {{ const w = {W}, c = w.cameras.main, p = w.player.sprite; return [Math.round((p.x - c.worldView.x) * c.zoom), Math.round((p.y - c.worldView.y) * c.zoom), c.zoom]; }})()"))
    await t.wait(90); await t.shot('rustle_b'); await t.p.keyboard.up('ArrowUp')
    await t.wait(1500); await t.shot('wind_1'); await t.wait(700); await t.shot('wind_2')


# ── Sept 27 batch: old save upgrade, battle info, learn screen, Move Reminder, Twinklit ──
PROMPT = "window.__tiamat.game.scene.getScene('Battle').children.list.some(o => o.visible && typeof o.text === 'string' && o.text.startsWith('What will'))"

async def batch3(t, port):
    await t.p.goto(f'http://localhost:{port}/')
    await wait_for(t, "window.__tiamat && window.__tiamat.game.scene.isActive('Title')", 30000, 'title')
    await t.js("""(() => { const T = window.__tiamat; const s = T.state.newState();
      s.player.name = 'Jamie'; s.player.map = 'saltreach'; s.player.x = 20; s.player.y = 20; s.sigils = ['moss', 'tide'];
      s.flags.got_nyxen = true; s.flags.got_index = true; s.flags.got_starter = true; s.vars.starter = 'cindlet'; s.bag.xp_share = 1; s.xpShareOn = true;
      const lead = T.createMon('cindreaver', 22, { sex: 'm' }); const nyx = T.createMon('nyxen', 12, { sex: 'f', ivs: { hp: 25, atk: 22, def: 30, spa: 28, spd: 21, spe: 27 } }); nyx.ot = 'Jamie';
      const hurt = T.createMon('beakling', 14); hurt.hp = 1; hurt.metMap = 'route1';
      s.party = [lead, T.createMon('zaplet', 20, { metMap: 'route3' })]; s.boxes[0].slots[0] = nyx; s.boxes[0].slots[1] = hurt;
      s.index = { seen: ['cindlet', 'cindreaver', 'nyxen', 'beakling', 'zaplet'], caught: ['cindlet', 'cindreaver', 'nyxen', 'beakling', 'zaplet'] };
      delete s.rev; delete s.mythicSwap; s.party.concat(s.boxes[0].slots.filter(Boolean)).forEach(m => delete m.learned);
      localStorage.setItem(T.state.slotKey(0), JSON.stringify(s)); })()""")
    await t.p.reload(); await t.wait(1500)
    await wait_for(t, "window.__tiamat.game.scene.isActive('Title')", 30000, 'title')
    print('loaded:', await t.js("window.__tiamat.state.loadGame(0)"), 'backup kept:', await t.js("!!localStorage.getItem(window.__tiamat.state.slotKey(0) + '.bak')"))
    print('box:', await t.js("JSON.stringify(window.__tiamat.G.state.boxes[0].slots.slice(0, 2).map(m => [m.species, m.level, m.sex, m.hp, m.moves.map(x => x.id).join('/')]))"))
    await t.js("(() => { const G = window.__tiamat.G; G.settings.textSpeed = 'instant'; window.__tiamat.game.scene.getScene('Title').scene.start('World'); })()")
    await wait_for(t, f"{W}.player", 30000, 'world')
    await t.wait(800)
    # a Tamer battle: foe team capsules, move menu, team menu
    await t.js(f"void {W}.S.battle('r3_poacher_b')")
    for _ in range(12):
        if await t.js(PROMPT): break
        await t.key('z', 60, 450)
    await t.shot('battle_hud')
    await t.key('z', 60, 400); await t.shot('move_menu'); await t.key('x', 60, 300)
    await t.key('ArrowDown', 60, 200); await t.key('z', 60, 500); await t.shot('team_picker'); await t.key('x', 60, 300)
    # the learn-a-move screen
    await t.js("(() => { const B = window.__tiamat.game.scene.getScene('Battle'); const m = window.__tiamat.G.state.party[0]; while (m.moves.length < 4) m.moves.push({ id: 'ember_fang', pp: 1, max: 25 }); window.__learn = B.learnPrompt(B.battle, m, 'dusk_ignite'); })()")
    await t.key('z', 60, 600); await t.shot('learn_screen')
    await t.key('ArrowUp', 60, 200); await t.shot('learn_screen_old')
    await t.key('x', 60, 300); await t.key('z', 60, 400); await t.key('z', 60, 400)
    await t.js("(() => { const B = window.__tiamat.game.scene.getScene('Battle'); if (B.scene.isActive()) { B.cfg.onEnd({ outcome: 'fled' }); B.scene.stop(); } })()")
    await t.wait(1200)
    # Move Reminder from the pause menu: Team -> first Morph -> Moves
    await t.key('c', 60, 700); await t.key('z', 60, 600); await t.key('z', 60, 500); await t.key('ArrowDown', 60, 200); await t.key('z', 60, 700)
    await t.shot('move_reminder')
    for _ in range(4): await t.key('x', 60, 300)
    # Aldous gives a level-5 Twinklit in a fresh save
    await t.js("(() => { const G = window.__tiamat.G; delete G.state.flags.got_nyxen; G.state.party = G.state.party.slice(0, 1); })()")
    await t.js(AUTO)
    await goto(t, 'brindlewood', 10, 10, 'down')
    await run_script(t, 'brindlewood.aldous')
    print('aldous gift:', await t.js("JSON.stringify(window.__tiamat.G.state.party.map(m => [m.species, m.level, m.moves.map(x => x.id).join('/')]))"))
    await t.js("clearInterval(window.__auto); window.__tiamat.input.keysDown.delete('confirm')")
    await t.js(f"(() => {{ const w = {W}; w.scene.launch('Menu', {{ mode: 'index', species: 'seraphelis', onClose: () => {{}} }}); w.scene.bringToTop('Menu'); }})()")
    await t.wait(1200); await t.shot('index_seraphelis')
    await t.key('ArrowUp', 60, 300); await t.key('ArrowUp', 60, 300); await t.shot('index_twinklit')


async def batch3b(t, port):
    await t.p.goto(f'http://localhost:{port}/?map=brindlewood&x=10&y=10&debug')
    await wait_for(t, f"window.__tiamat && {W}.player", 40000, 'world')
    await t.wait(800)
    await t.js("""(() => { const T = window.__tiamat, G = T.G; G.settings.textSpeed = 'instant';
      const m = T.createMon('lumelynx', 32, { sex: 'f' }); m.learned = ['glimmer_kiss', 'dream_tap']; G.state.party = [m];
      G.state.sigils = ['moss']; G.state.flags.got_starter = true; G.state.flags.got_index = true; })()""")
    # learn screen (as when a level-up wants a 5th move)
    await t.js(f"(() => {{ const T = window.__tiamat; window.__pick = T.pickMove({W}, T.G.state.party[0], {{ title: 'Which move should Lumelynx forget to learn Dreamshatter?', newMove: 'dreamshatter', owner: 'world' }}); }})()")
    await t.wait(600); await t.shot('learn_screen')
    await t.key('ArrowUp', 60, 250); await t.shot('learn_screen_old')
    await t.key('x', 60, 400)
    print('learn result:', await t.js("window.__pick"))
    # Move Reminder list
    print('can remember:', await t.js("window.__tiamat.rememberableMoves(window.__tiamat.G.state.party[0]).join(', ')"))
    await t.js(f"(() => {{ const T = window.__tiamat; const m = T.G.state.party[0]; window.__pick2 = T.pickMove({W}, m, {{ title: 'Which move should Lumelynx remember?', choices: T.rememberableMoves(m), owner: 'world' }}); }})()")
    await t.wait(600); await t.shot('move_reminder')
    await t.key('x', 60, 400)
    # Aldous
    await t.js(AUTO)
    await run_script(t, 'brindlewood.aldous')
    print('aldous gift:', await t.js("JSON.stringify(window.__tiamat.G.state.party.map(m => [m.species, m.level, m.moves.map(x => x.id).join('/')]))"))
    await t.js("clearInterval(window.__auto); window.__tiamat.input.keysDown.delete('confirm')")
    await t.js(f"(() => {{ const w = {W}; w.scene.launch('Menu', {{ mode: 'index', species: 'twinklit', onClose: () => {{}} }}); w.scene.bringToTop('Menu'); }})()")
    await t.wait(1200); await t.shot('index_twinklit')


async def poachers(t, port):
    await t.p.goto(f'http://localhost:{port}/?map=route3&x=8&y=17&debug')
    await wait_for(t, f"window.__tiamat && {W}.player", 40000, 'world')
    await t.wait(800)
    await t.js("""(() => { const T = window.__tiamat, G = T.G; G.settings.textSpeed = 'instant'; G.settings.battleAnims = false;
      G.state.vars.starter = 'cindlet'; G.state.flags.got_starter = true; G.state.party = [T.createMon('cindreaver', 40, { moves: ['umbral_flare', 'blaze_mane', 'ember_fang', 'shadow_spark'] })]; })()""")
    await t.js(f"{W}.refreshNpcs()")
    await t.js(AUTO)
    for tid in ['r3_poacher_a', 'r3_poacher_b']:
        print('npcs:', await t.js(f"{W}.mapView.id + ' ' + {W}.npcs.map(n => n.id).join(',')"))
        await t.js(f"(() => {{ const w = {W}; const n = w.npcById('{tid}'); w.player.setFace('down'); if (n) void w.talkTo(n); }})()")
        await t.wait(600)
        await idle(t, 60000, tid)
        print(tid, 'map:', await t.js(f"{W}.mapView.id"), 'beaten:', await t.js(f"!!window.__tiamat.G.state.defeated['{tid}']"), 'visible:', await t.js(f"(() => {{ const n = {W}.npcById('{tid}'); return n ? n.active : 'no npc'; }})()"))
    print('fled flag:', await t.js("!!window.__tiamat.G.state.flags.r3_poachers_fled"))
    await t.shot('after_poachers')
    await run_script(t, 'rescue.puddlet')
    print('puddlet:', await t.js("!!window.__tiamat.G.state.flags.rescued_puddlet"))


# ── every move's animation: plays all of them in a battle, screenshots a few mid-flight ──
B = "window.__tiamat.game.scene.getScene('Battle')"

async def moveanims(t, port):
    await t.p.goto(f'http://localhost:{port}/?map=route1&x=8&y=26&debug')
    await wait_for(t, f"window.__tiamat && {W}.player", 40000, 'world')
    await t.wait(600)
    await t.js("(() => { const T = window.__tiamat; T.G.settings.textSpeed = 'instant'; T.G.state.party = [T.createMon('cindreaver', 30)]; })()")
    await t.js(f"void {W}.S.wild('lambkin', 20)")
    for _ in range(12):
        if await t.js(PROMPT): break
        await t.key('z', 60, 450)
    shots = ['moonbeam_pounce', 'cosmic_insight', 'black_pyre', 'primordial_tide', 'champions_gauntlet', 'eye_of_the_storm',
             'ember_fang', 'thunder_arc', 'whiteout_gale', 'rubble_fall', 'psy_blast', 'hydro_burst', 'scythe_rend', 'heal_bud']
    for mid in shots:
        await t.js(f"(() => {{ const b = {B}.battle; window.__a = {B}.moveAnim(b, b.p, b.e, window.__tiamat.MOVES['{mid}']); }})()")
        await t.wait(330 if mid not in ('moonbeam_pounce', 'cosmic_insight', 'primordial_tide') else 650)
        await t.shot(f'fx_{mid}')
        await t.js("window.__a")
        await t.wait(900)
    # enemy attacking the player
    await t.js(f"(() => {{ const b = {B}.battle; window.__a = {B}.moveAnim(b, b.e, b.p, window.__tiamat.MOVES['glacier_surge']); }})()")
    await t.wait(360); await t.shot('fx_enemy_glacier_surge'); await t.wait(900)
    # every move, both directions, collecting errors
    await t.js(f"""(() => {{ const T = window.__tiamat, B = {B}, b = B.battle; window.__errs = []; window.__done = 0;
      const orig = console.warn; console.warn = (...a) => {{ if (String(a[0]).includes('moveFx')) window.__errs.push(a.join(' ')); orig(...a); }};
      B.animOn = true;
      (async () => {{ for (const id of Object.keys(T.MOVES)) {{ try {{ await B.moveAnim(b, window.__done % 2 ? b.e : b.p, window.__done % 2 ? b.p : b.e, T.MOVES[id]); }} catch (e) {{ window.__errs.push(id + ': ' + e); }}
        window.__done++; }} }})(); }})()""")
    await wait_for(t, "window.__done >= Object.keys(window.__tiamat.MOVES).length", 400000, 'all moves')
    print('moves animated:', await t.js("window.__done"), 'errors:', await t.js("JSON.stringify(window.__errs.slice(0, 10))"))
    print('sprites back in place:', await t.js(f"(() => {{ const B = {B}; return [Math.round(B.playerSpr.x), Math.round(B.playerSpr.y), B.playerSpr.alpha, Math.round(B.enemySpr.x), Math.round(B.enemySpr.y), B.enemySpr.alpha, B.children.list.length]; }})()"))


async def moveanims2(t, port):
    await t.p.goto(f'http://localhost:{port}/?map=route1&x=8&y=26&debug')
    await wait_for(t, f"window.__tiamat && {W}.player", 40000, 'world')
    await t.wait(600)
    await t.js("(() => { const T = window.__tiamat; T.G.settings.textSpeed = 'instant'; T.G.state.party = [T.createMon('cindreaver', 30)]; })()")
    await t.js(f"void {W}.S.wild('lambkin', 20)")
    for _ in range(12):
        if await t.js(PROMPT): break
        await t.key('z', 60, 450)
    for mid in ['moonbeam_pounce', 'guillotine_scythe', 'siege_ram', 'glimmer_kiss', 'tesla_coil', 'maelstrom']:
        await t.js(f"(() => {{ const b = {B}.battle; window.__a = {B}.moveAnim(b, b.p, b.e, window.__tiamat.MOVES['{mid}']); }})()")
        for ms in (200, 450, 750):
            await t.wait(250 if ms > 200 else 200)
            await t.shot(f'{mid}_{ms}')
        await t.js("window.__a"); await t.wait(1000)


async def skiffmap(t, port):
    await t.p.goto(f'http://localhost:{port}/?map=route3&x=8&y=17&debug')
    await wait_for(t, f"window.__tiamat && {W}.player", 40000, 'world')
    await t.wait(800)
    # on the water in the Skiff
    await t.js(f"(() => {{ const w = {W}, p = w.player; window.__tiamat.G.state.player.surfing = true; p.warp(10, 23, 'left'); p.setSkiff(true); }})()")
    await t.wait(400); await t.shot('skiff_left')
    await t.js(f"{W}.player.setFace('down')"); await t.wait(200); await t.shot('skiff_down')
    await t.js(f"{W}.player.setFace('up')"); await t.wait(200); await t.shot('skiff_up')
    # the Reach Map: visited Rootmere, Brindlewood, Saltreach; Wing Whistle in the bag
    await t.js(f"""(() => {{ const G = window.__tiamat.G, w = {W}; w.player.setSkiff(false); G.state.player.surfing = false; w.player.warp(8, 17, 'down');
      ['rootmere', 'brindlewood', 'saltreach'].forEach((m) => G.state.flags['visited_' + m] = true); G.state.bag.wing_whistle = 1; G.state.bag.reach_map = 1;
      G.state.seenMaps = ['home_2f', 'rootmere', 'route1', 'brindlewood', 'route2', 'thornwild', 'saltreach', 'route3'];
      w.scene.launch('Menu', {{ mode: 'map', onClose: () => {{}} }}); w.scene.bringToTop('Menu'); }})()""")
    await t.wait(1200); await t.shot('map_here')
    await t.key('ArrowLeft', 60, 80); await t.shot('map_moving'); await t.wait(500); await t.shot('map_left')
    await t.key('ArrowUp', 60, 600); await t.shot('map_up')
    await t.key('ArrowRight', 60, 600); await t.shot('map_right')


async def loadmenu(t, port):
    await t.p.goto(f'http://localhost:{port}/?map=route1&x=8&y=26&debug')
    await wait_for(t, f"window.__tiamat && {W}.player", 40000, 'world')
    await t.wait(600)
    await t.js("""(() => { const T = window.__tiamat; const s = T.state.newState(); s.player.name = 'Jamie'; s.player.map = 'rootmere'; s.player.x = 12; s.player.y = 12;
      s.party = [T.createMon('cindlet', 9)]; s.flags.got_starter = true; s.playMs = 4000000; localStorage.setItem(T.state.slotKey(0), JSON.stringify(s));
      T.G.state.party = [T.createMon('beakling', 5)]; T.G.slot = 0; })()""")
    await t.key('c', 60, 700); await t.shot('menu')
    for _ in range(4): await t.key('ArrowDown', 60, 150)
    await t.key('z', 60, 600); await t.shot('load_slots')
    await t.key('z', 60, 600); await t.shot('load_confirm')
    await t.key('z', 60, 400)
    await wait_for(t, f"{W}.mapView && {W}.mapView.id === 'rootmere' && {W}.player", 20000, 'loaded rootmere')
    await t.wait(1200); await t.shot('after_load')
    print('after load:', await t.js(f"[{W}.mapView.id, {W}.player.tx, {W}.player.ty, window.__tiamat.G.state.player.name, window.__tiamat.G.state.party.map(m => m.species).join(), {W}.busy]"))
    await t.key('ArrowDown', 200, 400)
    print('can move:', await t.js(f"[{W}.player.tx, {W}.player.ty]"))


# ── Trial halls: adepts guard the gates, the Warden waits for all of them; beaten grunts walk away ──
async def trialgate(t, port):
    await t.p.goto(f'http://localhost:{port}/?map=gearhollow_trial&x=6&y=16&debug')
    await wait_for(t, f"window.__tiamat && {W}.player", 40000, 'world')
    await t.wait(800)
    await t.js("""(() => { const T = window.__tiamat, G = T.G; G.settings.textSpeed = 'instant'; G.settings.battleAnims = false;
      G.state.vars.starter = 'cindlet'; G.state.flags.got_starter = true; G.state.flags.ironworks_done = true;
      G.state.party = [T.createMon('cindreaver', 60, { moves: ['umbral_flare', 'blaze_mane', 'ember_fang', 'shadow_spark'] })]; })()""")
    await t.shot('hall')
    # the Warden turns you away while adepts are left
    await t.js(f"void {W}.run('gearhollow_trial.warden')")
    await t.wait(700)
    await t.shot('warden_refuses')
    await t.key('z', 60, 300); await t.key('z', 60, 300)
    await idle(t, 20000, 'refused')
    print('battle after refusal:', await t.js("!!window.__tiamat.game.scene.isActive('Battle')"), 'sigil:', await t.js("!!window.__tiamat.G.state.flags.sigil_spark"))
    await t.js(AUTO)
    await t.js(f"(() => {{ const w = {W}; const orig = w.checkTrainers.bind(w); window.__log = []; w.checkTrainers = () => {{ const r = orig(); window.__log.push(w.player.tx + ',' + w.player.ty + (w.player.moving ? 'm' : '') + (w.busy ? 'B' : '') + '=' + r); return r; }}; }})()")
    spotted = []
    for step in range(16):
        await t.key('ArrowUp', 200, 60)
        await t.wait(150)
        if not await t.js(f"{W}.busy === 0 && window.__tiamat.input.top() === 'world'"):
            await t.wait(250)
            if len(spotted) < 3: await t.shot(f'spotted_{len(spotted)}')
            await idle(t, 60000, 'adept battle')
            spotted.append(await t.js(f"{W}.player.tx + ',' + {W}.player.ty"))
        if await t.js(f"{W}.player.ty") <= 4: break
    print('stopped at:', spotted, await t.js("window.__log.join(' ')"))
    print('adepts beaten:', await t.js("['gh_adept_1','gh_adept_2','gh_adept_3'].map(id => !!window.__tiamat.G.state.defeated[id]).join(',')"))
    print('player at', await t.js(f"{W}.player.tx + ',' + {W}.player.ty"))
    await t.js(f"(() => {{ const w = {W}; w.player.setFace('up'); void w.talkTo(w.npcById('iskra')); }})()")
    await t.wait(600)
    await idle(t, 90000, 'warden')
    print('sigil after all adepts:', await t.js("!!window.__tiamat.G.state.flags.sigil_spark"))
    await t.shot('after_warden')
    # Saltreach pier: beaten acolytes walk off, then Brann heads off to his Trial
    await t.js("window.__tiamat.G.state.party.forEach((m) => window.__tiamat.healMon(m))")
    await t.js(f"{W}.S.warp('saltreach', 20, 25, 'down')")
    await t.wait(1200)
    await idle(t, 20000, 'saltreach')
    for tid in ['st_acolyte_1', 'st_acolyte_2']:
        before = await t.js(f"(() => {{ const n = {W}.npcById('{tid}'); return n.actor.tx + ',' + n.actor.ty; }})()")
        await t.js(f"(() => {{ const w = {W}; void w.trainerEncounter(w.npcById('{tid}'), false); }})()")
        await t.wait(500)
        await idle(t, 60000, tid)
        after = await t.js(f"(() => {{ const n = {W}.npcById('{tid}'); return n.actor.tx + ',' + n.actor.ty + ' active=' + n.active; }})()")
        print(tid, before, '->', after)
    await t.js(f"void {W}.run('saltreach.brann_docks', {{ npc: {W}.npcById('st_brann') }})")
    await t.wait(1500)
    await t.shot('brann_leaving')
    await idle(t, 30000, 'brann')
    print('brann:', await t.js(f"(() => {{ const n = {W}.npcById('st_brann'); return n.actor.tx + ',' + n.actor.ty + ' active=' + n.active; }})()"), 'docks_done:', await t.js("!!window.__tiamat.G.state.flags.docks_done"))


async def trialdbg(t, port):
    await t.p.goto(f'http://localhost:{port}/?map=gearhollow_trial&x=6&y=13&debug')
    await wait_for(t, f"window.__tiamat && {W}.player", 40000, 'world')
    await t.wait(800)
    await t.js("""(() => { const T = window.__tiamat, G = T.G; G.settings.textSpeed = 'instant'; G.state.defeated.gh_adept_1 = true;
      G.state.party = [T.createMon('cindreaver', 60)]; })()""")
    print('adept2', await t.js(f"(() => {{ const n = {W}.npcById('gh_adept_2'); return [n.actor.tx, n.actor.ty, n.actor.face, n.active, n.def.sight, n.def.trainer].join(','); }})()"))
    await t.js(f"(() => {{ const w = {W}; const orig = w.checkTrainers.bind(w); window.__log = []; w.checkTrainers = () => {{ const r = orig(); window.__log.push(w.player.tx + ',' + w.player.ty + (w.player.moving ? 'm' : '') + '=' + r); return r; }}; }})()")
    await t.key('ArrowUp', 1400, 100)
    print('pos', await t.js(f"{W}.player.tx + ',' + {W}.player.ty + ' busy=' + {W}.busy"), await t.js("window.__log.join(' ')"))
    await t.shot('dbg')


# ── music after battles: exactly one track left playing, and it's the map's ──
MUS = "(() => { const a = window.__tiamat.audio; return a.musicKey + ' | ' + [...a.allMusic].map((m) => m.key + (m.isPlaying ? ':on' : ':off') + ':' + m.volume.toFixed(2)).join(', '); })()"

async def musicleak(t, port):
    await t.p.goto(f'http://localhost:{port}/?map=route1&x=16&y=10&debug')
    await wait_for(t, f"window.__tiamat && {W}.player", 40000, 'world')
    await t.p.mouse.click(400, 300)   # user gesture: unlock audio
    await t.wait(1500)
    await t.js("""(() => { const T = window.__tiamat, G = T.G; G.settings.textSpeed = 'instant'; G.settings.battleAnims = false;
      G.state.party = [T.createMon('cindreaver', 60, { moves: ['blaze_mane', 'ember_fang'] })]; })()""")
    print('ctx:', await t.js("window.__tiamat.game.sound.context.state"), 'before:', await t.js(MUS))
    await t.js(AUTO)
    for kind in ["S.wild('beakling', 3)", "S.battle('r1_theo')"]:
        await t.js(f"void {W}.{kind}")
        await t.wait(2500)
        print('in battle:', await t.js(MUS))
        await idle(t, 60000, 'battle end')
        await t.wait(1200)
        print('after:', await t.js(MUS))


# ── streaming music: tracks arrive in the background, only a few stay decoded, handovers are clean ──
async def audiocheck(t, port):
    await t.p.goto(f'http://localhost:{port}/')
    await wait_for(t, "window.__tiamat && window.__tiamat.game.scene.isActive('Title')", 40000, 'title')
    await t.p.mouse.click(400, 300)
    await t.wait(1500)
    print('title:', await t.js(MUS))
    await t.p.goto(f'http://localhost:{port}/?map=route1&x=16&y=10&debug')
    await wait_for(t, f"window.__tiamat && {W}.player", 40000, 'world')
    await t.p.mouse.click(400, 300)
    ok = await wait_for(t, "window.__tiamat.audio.music && window.__tiamat.audio.music.isPlaying", 20000, 'route music')
    print('route playing:', ok, await t.js(MUS))
    await t.js("""(() => { const T = window.__tiamat, G = T.G; G.settings.textSpeed = 'instant'; G.settings.battleAnims = false;
      G.state.party = [T.createMon('cindreaver', 60, { moves: ['blaze_mane', 'ember_fang'] })]; })()""")
    await t.js(AUTO)
    await t.js(f"void {W}.S.battle('r1_theo')")
    await t.wait(3000)
    print('battle:', await t.js(MUS))
    await idle(t, 60000, 'battle end')
    await t.wait(1500)
    print('after:', await t.js(MUS))
    await t.wait(20000)
    print('downloaded:', await t.js("window.__tiamat.audio.bytes.size"), 'decoded:', await t.js("window.__tiamat.audio.decoded.join(',')"))
    for k in ['cursor', 'select', 'spotted', 'hit_super', 'ui_text', 'sig_black_pyre', 'mv_fire', 'jingle_heal']:
        print(k, await t.js(f"window.__tiamat.game.cache.audio.exists('{k}')"))


async def voldbg(t, port):
    await t.p.goto(f'http://localhost:{port}/?map=route1&x=16&y=10&debug')
    await wait_for(t, f"window.__tiamat && {W}.player", 40000, 'world')
    await t.p.mouse.click(400, 300)
    for i in range(8):
        print(await t.js("(() => { const a = window.__tiamat.audio; return [window.__tiamat.G.settings.musicVol, a.duck, a.musicVolume(), a.music && a.music.volume, a.allMusic.size].join(' '); })()"))
        await t.wait(700)


async def unstick(t, port):
    # a save made where a rope barrier now stands puts you on the nearest free tile
    await t.p.goto(f'http://localhost:{port}/?map=gearhollow_trial&x=2&y=8&debug')
    await wait_for(t, f"window.__tiamat && {W}.player", 40000, 'world')
    await t.wait(800)
    print('placed at', await t.js(f"{W}.player.tx + ',' + {W}.player.ty + ' ' + {W}.mapView.behavior({W}.player.tx, {W}.player.ty)"))


# ── the reported bug: after a battle on the water (Route 5, after the 4th Sigil) the battle music kept playing ──
async def surfleak(t, port):
    await t.p.goto(f'http://localhost:{port}/?map=route5&x=15&y=11&debug')
    await wait_for(t, f"window.__tiamat && {W}.player", 40000, 'world')
    await t.p.mouse.click(400, 300)
    await t.js("""(() => { const T = window.__tiamat, G = T.G; G.settings.textSpeed = 'instant'; G.settings.battleAnims = false;
      G.state.party = [T.createMon('cindreaver', 85, { moves: ['shadow_spark', 'umbral_flare'] })];
      G.state.player.surfing = true; })()""")
    await t.js(f"(() => {{ const w = {W}; w.player.warp(15, 11, 'right'); w.player.setSkiff(true); }})()")
    await wait_for(t, "window.__tiamat.audio.music && window.__tiamat.audio.music.isPlaying", 20000, 'route5 music')
    for k in range(4):
        print('vol', await t.js("(() => { const m = window.__tiamat.audio.music; return m.volume + ' gain.value=' + m.volumeNode.gain.value + ' ctx=' + window.__tiamat.game.sound.context.state + ' t=' + window.__tiamat.game.sound.context.currentTime.toFixed(2); })()"))
        await t.wait(400)
    print('start:', await t.js(MUS))
    await t.js(AUTO)
    for i, d in enumerate(['ArrowUp', 'ArrowDown', 'ArrowUp']):
        before = await t.js(f"{W}.player.tx + ',' + {W}.player.ty")
        await t.js(f"(() => {{ const w = {W}; w.lastEnc = 10; window.__r = Math.random; Math.random = () => 0.001; setTimeout(() => {{ Math.random = window.__r; }}, 600); }})()")
        await t.key(d, 180, 100)
        print('moved', before, '->', await t.js(f"{W}.player.tx + ',' + {W}.player.ty + ' surf=' + window.__tiamat.G.state.player.surfing + ' ' + {W}.mapView.behavior({W}.player.tx, {W}.player.ty)"))
        ok = await wait_for(t, "window.__tiamat.game.scene.isActive('Battle')", 8000, 'battle start')
        await t.wait(2500)
        if i == 1:   # a level-up jingle in the middle of the battle
            await t.js("void window.__tiamat.audio.jingle('jingle_level')")
            await t.wait(300)
        print(f'battle {i}:', ok, await t.js(MUS))
        await idle(t, 90000, 'battle end')
        print(f'  right after:', await t.js(MUS))
        await t.wait(3000)
        print(f'  3s later:', await t.js(MUS))
    # walk off the water and back into Frostspire's music
    await t.js(f"{W}.S.warp('frostspire', 20, 14, 'down')")
    await t.wait(4000)
    print('frostspire:', await t.js(MUS))
