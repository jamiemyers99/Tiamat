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
    await t.p.goto(f'http://localhost:{port}/?map=route1&x=16&y=4&debug')
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
    await goto(t, 'brindlewood_trial', 8, 3, 'up')
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
    await goto(t, 'saltreach_trial', 8, 3, 'up')
    await run_script(t, 'saltreach_trial.warden')
    await goto(t, 'coldforge_mines', 39, 21, 'up')
    await t.shot('mines')
    await run_script(t, 'mines.vesk')
    await t.js("(() => { const d = window.__tiamat.G.state.defeated; d.iw_acolyte_1 = d.iw_acolyte_2 = d.iw_acolyte_3 = true; })()")
    await goto(t, 'gearhollow_ironworks', 10, 4, 'up')
    await run_script(t, 'ironworks.iskra')
    await goto(t, 'gearhollow_trial', 8, 3, 'up')
    await run_script(t, 'gearhollow_trial.warden')
    await goto(t, 'gearhollow', 27, 25, 'down')
    await run_script(t, 'gearhollow.wren')
    # Act III
    await goto(t, 'hollowmere_trial', 10, 3, 'up')
    await run_script(t, 'hollowmere_trial.warden')
    await goto(t, 'hollowmere', 14, 16, 'left')
    await run_script(t, 'hollowmere.shore')
    await t.shot('hollowmere')
    # Act IV
    await goto(t, 'frostspire_trial', 9, 3, 'up')
    await run_script(t, 'frostspire_trial.warden')
    await goto(t, 'riftgate_trial', 10, 3, 'up')
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
                             ('riftgate', 20, 19, 21), ('route6', 30, 20, 12), ('thornwild', 27, 30, 15), ('abyssal_rift', 20, 8, 12), ('route4', 27, 30, 17)]:
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
      s.player.name = 'Jamie'; s.player.map = 'route1'; s.player.x = 16; s.player.y = 4;
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
    # (the halls are puzzles now: see `trials`, which walks every one in the real game)
    await solve_trial(t, port, 'gearhollow_trial', 'sigil_spark')


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
    await t.p.goto(f'http://localhost:{port}/?map=route1&x=16&y=4&debug')
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
    await t.p.goto(f'http://localhost:{port}/?map=route1&x=16&y=4&debug')
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
    await t.p.goto(f'http://localhost:{port}/?map=route1&x=16&y=4&debug')
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


# ── PC storage: flip boxes, carry a Morph between boxes, swap, withdraw / deposit, box options ──
async def pcbox(t, port):
    await t.p.goto(f'http://localhost:{port}/?map=rootmere&x=16&y=8&debug')
    await wait_for(t, f"window.__tiamat && {W}.player", 40000, 'world')
    await t.wait(800)
    await t.js("""(() => { const T = window.__tiamat, G = T.G; G.settings.textSpeed = 'instant';
      const faint = T.createMon('beakling', 12); faint.hp = 0;
      G.state.party = [T.createMon('cindlet', 20), faint];
      const b = G.state.boxes;
      [['nibbit', 5, 0], ['trotter', 9, 1], ['pebbling', 14, 2], ['chittik', 6, 7], ['puddlet', 11, 12]].forEach(([s, l, k]) => { b[0].slots[k] = T.createMon(s, l); });
      b[1].slots[3] = T.createMon('burrlet', 8); b[1].slots[4] = T.createMon('beakling', 4);
      G.state.pcBox = 0; })()""")
    count = "(() => { const S = window.__tiamat.G.state; return S.party.length + S.boxes.reduce((n, b) => n + b.slots.filter(Boolean).length, 0); })()"
    total0 = await t.js(count)
    where = lambda b, k: t.js(f"(() => {{ const m = window.__tiamat.G.state.boxes[{b}].slots[{k}]; return m ? m.species : null; }})()")
    await t.js(f"void {W}.S.openScreen('storage')")
    await t.wait(900)
    await t.shot('pc_open')
    print('top:', await t.top())
    # flip boxes from the box name
    await t.key('ArrowUp'); await t.shot('on_header')
    await t.key('ArrowRight'); await t.wait(250); await t.shot('box2')
    print('after right on header, pcBox =', await t.js("window.__tiamat.G.state.pcBox"))
    await t.key('ArrowLeft'); await t.key('ArrowDown')
    # carry Nibbit from Box 1 slot 0 to Box 3 slot 0
    await t.key('z', 60, 300); await t.shot('mon_menu'); await t.key('z', 60, 300)
    await t.shot('carrying')
    await t.key('ArrowUp'); await t.key('ArrowRight'); await t.key('ArrowRight'); await t.wait(200)
    await t.shot('carrying_box3')
    await t.key('ArrowDown'); await t.key('z', 60, 300)
    print('box1[0] =', await where(0, 0), ' box3[0] =', await where(2, 0))
    await t.shot('placed_box3')
    # PgUp back to Box 1 and swap Trotter (slot 1) onto Pebbling (slot 2), then back out
    await t.key('PageUp'); await t.key('PageUp'); await t.wait(200)
    await t.key('ArrowRight'); await t.key('z', 60, 300); await t.key('z', 60, 300)
    await t.key('ArrowRight'); await t.key('z', 60, 300)
    await t.shot('swapped_holding_pebbling')
    print('after swap: slot1', await where(0, 1), 'slot2', await where(0, 2))
    await t.key('x', 60, 300)
    print('after put back: slot0', await where(0, 0), 'slot1', await where(0, 1), 'slot2', await where(0, 2))
    # withdraw Pebbling (slot 1) into the team
    await t.key('ArrowLeft'); await t.key('z', 60, 300); await t.key('ArrowDown'); await t.key('ArrowDown'); await t.key('z', 60, 300)
    print('party after withdraw:', await t.js("window.__tiamat.G.state.party.map(m => m.species).join()"))
    await t.shot('withdrawn')
    # the only healthy team member can't be lifted
    await t.js("window.__tiamat.G.state.party[2].hp = 0")
    for _ in range(5): await t.key('ArrowRight')
    await t.key('z', 60, 300); await t.key('z', 60, 300)
    await t.shot('last_healthy_blocked')
    print('held after trying to lift the last healthy:', await t.js("window.__tiamat.G.state.party.length"))
    await t.js("window.__tiamat.healMon(window.__tiamat.G.state.party[2])")
    # deposit Beakling (team row 1)
    await t.key('ArrowDown'); await t.key('z', 60, 300); await t.key('ArrowDown'); await t.key('ArrowDown'); await t.key('z', 60, 400)
    print('party after deposit:', await t.js("window.__tiamat.G.state.party.map(m => m.species).join()"), '| beakling healed in box:', await t.js("window.__tiamat.G.state.boxes[0].slots.filter(Boolean).some(m => m.species === 'beakling' && m.hp > 0)"))
    await t.shot('deposited')
    # summary from the box with the info key, flip to the next Morph
    for _ in range(6): await t.key('ArrowLeft')
    await t.key('r', 60, 500); await t.shot('summary'); await t.key('ArrowDown', 60, 300); await t.shot('summary_next'); await t.key('x', 60, 400)
    await t.shot('after_summary')
    # box options: wallpaper, sort by level, jump
    await t.key('ArrowUp')
    print('still in the PC:', await t.js("window.__tiamat.input.top()"))
    await t.key('z', 60, 300); await t.shot('box_options')
    await t.key('ArrowDown'); await t.key('ArrowDown'); await t.key('z', 60, 300)
    for _ in range(7): await t.key('ArrowDown', 60, 150)
    await t.shot('wallpaper_night'); await t.key('z', 60, 300)
    print('wall:', await t.js("window.__tiamat.G.state.boxes[0].wall"))
    await t.key('z', 60, 300); await t.key('ArrowDown'); await t.key('ArrowDown'); await t.key('ArrowDown'); await t.key('z', 60, 300); await t.key('ArrowDown'); await t.key('z', 60, 300)
    print('sorted by level:', await t.js("window.__tiamat.G.state.boxes[0].slots.slice(0, 6).map(m => m ? m.species + m.level : '-').join()"))
    await t.shot('sorted')
    await t.key('z', 60, 300); await t.key('z', 60, 300)
    for _ in range(5): await t.key('ArrowDown', 60, 150)
    await t.shot('jump_list'); await t.key('z', 60, 300)
    print('jumped to box', await t.js("window.__tiamat.G.state.pcBox"))
    await t.shot('jumped')
    # rename it
    await t.key('z', 60, 300); await t.key('ArrowDown'); await t.key('z', 60, 400)
    for _ in range(6): await t.key('Backspace', 40, 60)
    for ch in 'Keepers': await t.key(ch, 40, 60)
    await t.key('Enter', 60, 400)
    print('renamed:', await t.js("window.__tiamat.G.state.boxes[window.__tiamat.G.state.pcBox].name"))
    # lift a Morph, then close the PC entirely: nothing may be lost
    await t.key('PageUp'); await t.key('PageUp'); await t.key('PageUp'); await t.key('PageUp'); await t.key('PageUp')
    await t.key('ArrowDown'); await t.key('z', 60, 300); await t.key('z', 60, 300)
    await t.key('x', 60, 300); await t.key('x', 60, 500)
    print('top after close:', await t.top(), '| Morphs before', total0, 'after', await t.js(count))
    await t.shot('closed')


# ── Route 6: walk the pass from Frostspire to Riftgate; every trainer must stop you ──
async def route6walk(t, port):
    import trainer_gates as tg
    await t.p.goto(f'http://localhost:{port}/?map=route6&x=1&y=16&debug')
    await wait_for(t, f"window.__tiamat && {W}.player", 40000, 'world')
    await t.wait(800)
    await t.js("""(() => { const T = window.__tiamat, G = T.G; G.settings.textSpeed = 'instant'; G.settings.battleAnims = false;
      G.state.flags.sigil_rime = true; G.state.flags.got_starter = true; G.state.vars.starter = 'cindlet';
      G.state.party = [T.createMon('cindreaver', 100, { moves: ['hydro_burst', 'grand_slam', 'riftbreaker', 'umbral_flare'] })];
      G.state.party[0].moves.forEach((mv) => { mv.pp = 999; mv.max = 999; }); })()""")
    await t.js(AUTO)
    keymap = {'up': 'ArrowUp', 'down': 'ArrowDown', 'left': 'ArrowLeft', 'right': 'ArrowRight'}
    async def walk(mid, goal, label, limit=260):
        battles = []
        for _ in range(limit):
            pos = await t.js(f"[{W}.mapView.id, {W}.player.tx, {W}.player.ty]")
            if pos[0] != mid or (pos[1], pos[2]) == goal: return battles, pos
            steps = tg.route(mid, (pos[1], pos[2]), goal)
            if not steps: print('no route from', pos); return battles, pos
            await t.key(keymap[steps[0]], 170, 40)
            for _ in range(20):
                if not await t.js(f"{W}.player.moving"): break
                await t.wait(40)
            if not await t.js(f"{W}.busy === 0 && window.__tiamat.input.top() === 'world'"):
                await t.wait(300)
                who = await t.js(f"(() => {{ const w = {W}; const n = w.npcs.find(n => n.def.trainer && !window.__tiamat.G.state.defeated[n.def.trainer] && Math.abs(n.actor.tx - w.player.tx) + Math.abs(n.actor.ty - w.player.ty) <= 5); return n ? n.def.trainer : '?'; }})()")
                if len(battles) < 5: await t.shot(f'{label}_spotted_{len(battles)}')
                await idle(t, 90000, 'battle')
                battles.append((who, pos[1], pos[2]))
        return battles, await t.js(f"[{W}.mapView.id, {W}.player.tx, {W}.player.ty]")
    await wait_for(t, f"{W}.mapView.id === 'route6' && {W}.busy === 0", 20000, 'route6')
    await t.wait(600)
    await t.shot('route6_start')
    print('entered route6 at', await t.js(f"[{W}.player.tx, {W}.player.ty]"))
    battles, end = await walk('route6', (53, 14), 'east')
    print('eastbound battles:', battles)
    print('reached:', end)
    print('defeated:', await t.js("['r6_skier_1','r6_skier_2','r6_hiker','r6_acolyte','r6_ace'].map(id => id + '=' + !!window.__tiamat.G.state.defeated[id]).join(' ')"))
    await t.key('ArrowRight', 600, 60)
    await wait_for(t, f"{W}.mapView.id === 'riftgate'", 15000, 'riftgate')
    await t.wait(900)
    print('now on', await t.js(f"[{W}.mapView.id, {W}.player.tx, {W}.player.ty]"))
    await t.shot('riftgate_arrival')
    # and back west again (ledges make the return quicker)
    for _ in range(12):
        if await t.js(f"{W}.mapView.id") == 'route6': break
        await t.key('ArrowLeft', 170, 250)
    await wait_for(t, f"{W}.mapView.id === 'route6' && {W}.busy === 0", 15000, 'back to route6')
    await t.wait(400)
    battles, end = await walk('route6', (0, 16), 'west')
    print('westbound battles:', battles, 'reached:', end)
    for _ in range(6):
        if await t.js(f"{W}.mapView.id") == 'frostspire': break
        await t.key('ArrowLeft', 170, 250)
    await wait_for(t, f"{W}.mapView.id === 'frostspire'", 15000, 'frostspire')
    print('back on', await t.js(f"[{W}.mapView.id, {W}.player.tx, {W}.player.ty]"))


# ── Lullaby Siphon (Twinklit line, Lv42): sleep + drain, then an easy catch ──
async def lullaby(t, port):
    await t.p.goto(f'http://localhost:{port}/?map=route6&x=18&y=16&debug')
    await wait_for(t, f"window.__tiamat && {W}.player", 40000, 'world')
    await t.wait(800)
    await t.js("""(() => { const T = window.__tiamat, G = T.G; G.settings.textSpeed = 'instant';
      const s = T.createMon('seraphelis', 42, { moves: ['lullaby_siphon', 'astral_purr', 'wishing_star', 'dreamshatter'] }); s.hp = Math.floor(s.hp / 2);
      G.state.party = [s]; G.state.bag.capsule = 5; })()""")
    await t.js(f"void {W}.S.wild('glaciursa', 36)")
    await t.wait(2600)
    for i in range(6): await t.key('z', 60, 350)
    await t.shot('menu')
    await t.key('z', 60, 400); await t.shot('moves')
    await t.key('z', 60, 250)
    for i in range(8):
        await t.wait(450)
        if i in (1, 3, 5): await t.shot(f'siphon_{i}')
        st = await t.js("(() => { const b = window.__tiamat.game.scene.getScene('Battle'); const e = b && b.battle && b.battle.e && b.battle.e.mon; return e ? [e.status, e.hp] : null; })()")
        if st and st[0] == 'sleep': break
    print('foe:', await t.js("(() => { const b = window.__tiamat.game.scene.getScene('Battle').battle; return [b.e.mon.status, b.e.mon.hp, b.p.mon.hp]; })()"))
    for i in range(10): await t.key('z', 60, 300)
    await t.shot('after')


# ── walk a route start → goal along the shortest legal path; report which trainers stopped you ──
async def walk_route(t, port, mid, start, goal, trainers, setup=''):
    import trainer_gates as tg
    await t.p.goto(f'http://localhost:{port}/?map={mid}&x={start[0]}&y={start[1]}&debug')
    await wait_for(t, f"window.__tiamat && {W}.player", 40000, 'world')
    await t.wait(800)
    await t.js("""(() => { const T = window.__tiamat, G = T.G; G.settings.textSpeed = 'instant'; G.settings.battleAnims = false;
      G.state.flags.got_starter = true; G.state.vars.starter = 'cindlet';
      G.state.party = [T.createMon('cindreaver', 100, { moves: ['hydro_burst', 'grand_slam', 'riftbreaker', 'umbral_flare'] })];
      G.state.party[0].moves.forEach((mv) => { mv.pp = 999; mv.max = 999; }); })()""")
    if setup: await t.js(setup)
    await t.js(AUTO)
    keymap = {'up': 'ArrowUp', 'down': 'ArrowDown', 'left': 'ArrowLeft', 'right': 'ArrowRight'}
    stops = []
    for _ in range(400):
        pos = await t.js(f"[{W}.mapView.id, {W}.player.tx, {W}.player.ty]")
        if pos[0] != mid or (pos[1], pos[2]) == tuple(goal): break
        steps = tg.route(mid, (pos[1], pos[2]), goal)
        if not steps: print('no route from', pos); break
        await t.key(keymap[steps[0]], 170, 40)
        for _ in range(20):
            if not await t.js(f"{W}.player.moving"): break
            await t.wait(40)
        if not await t.js(f"{W}.busy === 0 && window.__tiamat.input.top() === 'world'"):
            before = await t.js("JSON.stringify(window.__tiamat.G.state.defeated)")
            await t.wait(300)
            if len(stops) < 3: await t.shot(f'{mid}_stopped_{len(stops)}')
            await idle(t, 120000, 'event')
            after = await t.js("JSON.stringify(window.__tiamat.G.state.defeated)")
            import json as _j
            new = [k for k in _j.loads(after) if k not in _j.loads(before)]
            stops.append((','.join(new) or 'event', pos[1], pos[2]))
            if len(stops) >= 3 and stops[-1] == stops[-2] == stops[-3]: print('stuck on a repeating event at', pos); break
    print(mid, 'stopped by:', stops)
    print(mid, 'reached:', await t.js(f"[{W}.mapView.id, {W}.player.tx, {W}.player.ty]"))
    print(mid, 'beaten:', await t.js("(" + repr(trainers) + ").map(id => id + '=' + !!window.__tiamat.G.state.defeated[id]).join(' ')"))


async def route1walk(t, port):
    await walk_route(t, port, 'route1', (16, 48), (16, 0), ['r1_ollie', 'r1_dana', 'r1_nell', 'r1_theo'])


async def route4walk(t, port):
    await walk_route(t, port, 'route4', (16, 52), (16, 0), ['r4_hiker', 'r4_lady', 'r4_mystic', 'r4_scholar', 'r4_ranger'])


async def thornwalk(t, port):
    await walk_route(t, port, 'thornwild', (1, 10), (30, 39), ['tw_bugs', 'tw_ranger', 'tw_mystic', 'tw_acolyte_1', 'tw_acolyte_2', 'rival2_cindlet'])


async def thorndbg(t, port):
    await t.p.goto(f'http://localhost:{port}/?map=thornwild&x=0&y=10&debug')
    await wait_for(t, f"window.__tiamat && {W}.player", 40000, 'world')
    await t.wait(1500)
    print(await t.js(f"{W}.npcs.map(n => n.def.id + '@' + n.actor.tx + ',' + n.actor.ty + ' ' + n.actor.face + ' active=' + n.active + ' tr=' + n.def.trainer + ' sight=' + n.def.sight).join(' | ')"))
    print(await t.js(f"[{W}.player.tx, {W}.player.ty, {W}.busy, window.__tiamat.input.top()]"))


# ── the new capsule art: ground item, Team menu icon, bag, foe pips, a throw, a send-out ──
async def capsulelook(t, port):
    B = "window.__tiamat.game.scene.getScene('Battle')"
    await t.p.goto(f'http://localhost:{port}/?map=route1&x=22&y=32&debug')
    await wait_for(t, f"window.__tiamat && {W}.player", 40000, 'world')
    await t.wait(1200)
    await t.js("""(() => { const T = window.__tiamat, G = T.G; G.settings.textSpeed = 'instant';
      G.state.flags.got_starter = true; G.state.vars.starter = 'cindlet';
      const a = T.createMon('cindreaver', 30); a.capsule = 'dusk_capsule';
      G.state.party = [a, T.createMon('beakling', 20)];
      Object.assign(G.state.bag, { capsule: 9, prime_capsule: 5, apex_capsule: 3, dusk_capsule: 4, swift_capsule: 2, covenant_capsule: 1 }); })()""")
    await t.shot('ground_item')
    await t.key('c', 60, 700); await t.shot('pause_menu')
    await t.key('ArrowDown'); await t.key('z', 60, 600)
    await t.key('ArrowRight', 60, 400); await t.shot('bag_capsules')
    for _ in range(3): await t.key('ArrowDown', 60, 200)
    await t.shot('bag_capsules_3')
    await t.key('x', 60, 400); await t.key('x', 60, 600)
    # a trainer battle: the foe's team pips, and our Morph coming out of its Dusk Capsule
    await t.js(f"void {W}.S.battle('r1_nell')")
    await t.wait(2600)
    for i in range(3): await t.key('z', 60, 250)
    await t.wait(150); await t.shot('send_out')
    await t.wait(1500); await t.shot('foe_pips')
    await t.p.goto(f'http://localhost:{port}/?map=route1&x=22&y=32&debug')
    await wait_for(t, f"window.__tiamat && {W}.player", 40000, 'world')
    await t.wait(900)
    for cap in ['prime_capsule', 'apex_capsule', 'swift_capsule', 'covenant_capsule']:
        await t.js("""(() => { const T = window.__tiamat, G = T.G; G.settings.textSpeed = 'instant'; G.state.party = [T.createMon('cindreaver', 30)]; })()""")
        await t.js(f"void {W}.S.wild('beakling', 5)")
        await t.wait(3200)
        await t.js(f"void {B}.capture({B}.battle, '{cap}', 2, false)")
        await t.wait(1250); await t.shot(f'throw_{cap}')
        await t.p.goto(f'http://localhost:{port}/?map=route1&x=22&y=32&debug')
        await wait_for(t, f"window.__tiamat && {W}.player", 40000, 'world')
        await t.wait(900)


# ── every Trial hall: walk the puzzle in the real game (solver plans each step), battle the adepts, win the Sigil ──
TRIALS = [('brindlewood_trial', 'sigil_moss'), ('saltreach_trial', 'sigil_tide'), ('gearhollow_trial', 'sigil_spark'),
          ('hollowmere_trial', 'sigil_veil'), ('frostspire_trial', 'sigil_rime'), ('riftgate_trial', 'sigil_wyrm')]


async def solve_trial(t, port, mid, sigil, shots=True):
    import puzzle_check as pc
    await t.p.goto(f'http://localhost:{port}/?map={mid}&x=1&y=1&debug')
    await wait_for(t, f"window.__tiamat && {W}.player", 40000, 'world')
    await t.wait(700)
    await t.js("""(() => { const T = window.__tiamat, G = T.G; G.settings.textSpeed = 'instant'; G.settings.battleAnims = false;
      G.state.flags.got_starter = true; G.state.vars.starter = 'cindlet'; G.state.flags.ironworks_done = true;
      G.state.party = [T.createMon('cindreaver', 100, { moves: ['hydro_burst', 'grand_slam', 'riftbreaker', 'umbral_flare'] })];
      G.state.party[0].moves.forEach((mv) => { mv.pp = 999; mv.max = 999; }); })()""")
    L, objs, _ = pc.load(mid)
    start = next((x, y - 1) for y, row in enumerate(L) for x, c in enumerate(row) if c == 'm')
    await t.js(f"{W}.transition('{mid}', {start[0]}, {start[1]}, 'up')")
    await t.wait(900)
    await t.js(AUTO)
    keymap = {'up': 'ArrowUp', 'down': 'ArrowDown', 'left': 'ArrowLeft', 'right': 'ArrowRight'}
    fights, n = [], 0
    for _ in range(300):
        st = await t.js(f"[{W}.player.tx, {W}.player.ty, Object.keys(window.__tiamat.G.state.flags).filter(f => /^(gh_flip|rg_a|rg_b)$/.test(f))]")
        plan = pc.analyse(mid, plan=((st[0], st[1]), set(st[2])))
        if plan is None: print(mid, 'NO PLAN from', st); break
        if not plan: break
        before = await t.js("Object.keys(window.__tiamat.G.state.defeated).length")
        await t.key(keymap[plan[0]], 150, 30)
        n += 1
        for _ in range(80):
            if await t.js(f"!{W}.player.moving && {W}.busy === 0 && window.__tiamat.input.top() === 'world'"): break
            await t.wait(60)
        if not await t.js(f"{W}.busy === 0 && window.__tiamat.input.top() === 'world'"):
            await idle(t, 90000, 'adept')
        after = await t.js("Object.keys(window.__tiamat.G.state.defeated).filter(k => /_adept_/.test(k)).join(',')")
        if await t.js("Object.keys(window.__tiamat.G.state.defeated).length") > before:
            fights.append(after.split(',')[-1])
            if shots and len(fights) == 1: await t.shot(f'{mid}_adept')
    pos = await t.js(f"[{W}.player.tx, {W}.player.ty]")
    if shots: await t.shot(f'{mid}_at_warden')
    await t.js(f"{W}.player.setFace('up')")
    await t.key('z', 60, 300)
    await idle(t, 120000, 'warden')
    beaten = await t.js("Object.keys(window.__tiamat.G.state.defeated).filter(k => /_adept_/.test(k)).length")
    got = await t.js(f'!!window.__tiamat.G.state.flags.{sigil}')
    print(f'{mid}: {n} presses, reached {pos}, adepts beaten: {beaten}, sigil: {got}')
    # once won, the hall powers down: the Warden's pad takes you out, and the one by the entrance takes you back in
    async def walk(goal, label):
        steps = 0
        for _ in range(40):
            here = await t.js(f"[{W}.player.tx, {W}.player.ty]")
            if tuple(here) == goal: break
            route = pc.analyse(mid, plan=(tuple(here), {sigil}, goal))
            if not route: print(mid, label, 'NO ROUTE from', here); break
            await t.key(keymap[route[0]], 150, 30)
            steps += 1
            await t.wait(500)
            await idle(t, 20000, label)
        return steps, await t.js(f"[{W}.player.tx, {W}.player.ty]")
    if shots: await t.shot(f'{mid}_pads')
    wx, wy = next((x, y) for (tp, x, y, a, kv) in objs if tp == 'npc' and kv.get('script', '').endswith('.warden'))
    print(f'   after winning: out', *(await walk(tuple(start), 'out')), ' back in', *(await walk((wx, wy + 1), 'in')))


async def trials(t, port):
    for mid, sigil in TRIALS:
        await solve_trial(t, port, mid, sigil)


# ── post-game: Index rewards, the Crown Challenge, the Old Door, Keeper Enna and hatching Abzurath ──
async def postgame(t, port):
    await t.p.goto(f'http://localhost:{port}/?map=marsh_lab&x=8&y=4&debug')
    await wait_for(t, f"window.__tiamat && {W}.player", 40000, 'world')
    await t.wait(800)
    G = 'window.__tiamat.G'
    await t.js(f"""(() => {{ const T = window.__tiamat, G = T.G; G.settings.textSpeed = 'instant'; G.settings.battleAnims = false;
      for (const f of ['got_starter', 'mum_boots', 'cradle_done', 'crown_scene', 'game_clear', 'woke_up']) G.state.flags[f] = true;
      G.state.money = 1000;
      G.state.party = [T.createMon('pyromane', 76), T.createMon('glaciursa', 76, {{ moves: ['icicle_jab', 'hail_volley', 'power_kick', 'all_out_slam'] }}),
        T.createMon('maelstrand', 76, {{ moves: ['rime_ray', 'hydro_burst', 'icicle_jab', 'undertow'] }}), T.createMon('mosswarden', 75, {{ moves: ['quake_stomp', 'timber_crash', 'bloom_blast', 'heal_bud'] }})];
      const ids = T.SPECIES_LIST ? T.SPECIES_LIST.map(s => s.id) : Object.keys(T.SPECIES);
      G.state.index.caught = ids.filter(id => !['abzurath'].includes(id)).slice(0, 60); }})()""")
    await t.js(AUTO)
    # 1) 60 caught: the 25 and 50 rewards
    await run_script(t, 'lab.marsh')
    print('after 60:', await t.js(f"[{G}.state.money, Object.keys({G}.state.flags).filter(f => f.startsWith('index_reward')).join(','), {G}.state.bag.td19, {G}.state.bag.td20, {G}.state.bag.td21, {G}.state.bag.apex_capsule]"))
    # 2) the whole Index: 75, 100 and the complete-Index prize
    await t.js(f"(() => {{ const T = window.__tiamat; const ids = Object.keys(T.SPECIES).filter(id => id !== 'abzurath'); T.G.state.index.caught = ids; }})()")
    await t.js("clearInterval(window.__auto)")
    await t.js(f"void {W}.run('lab.marsh')")
    for i in range(40):
        await t.key('z', 60, 180)
        if await t.js(f"!!{G}.state.bag.mystery_egg"): break
    await t.shot('marsh_egg')
    await t.js(AUTO)
    await idle(t, 60000, 'marsh done')
    print('after all:', await t.js(f"[{G}.state.money, Object.keys({G}.state.flags).filter(f => f.startsWith('index_reward')).join(','), {G}.state.bag.radiant_charm, {G}.state.bag.mystery_egg, {G}.state.bag.td26]"))
    # 3) the Crown Challenge, all seven rounds back to back
    await goto(t, 'spire_crown', 4, 5, 'left')
    print('round on entry:', await t.js(f"{G}.state.vars.crown_round"))
    await t.shot('crown')
    await t.js("window.__tiamat.G.state.party.forEach(m => { window.__tiamat.healMon(m); m.moves.forEach(mv => { mv.pp = 999; mv.max = 999; }); })")
    await t.js(f"void {W}.run('crown.warden', {{ npc: {W}.npcById('crown_mossa') }})")
    for r in range(8):
        ok = await wait_for(t, f"{G}.state.flags.crown_champion || !window.__tiamat.game.scene.isActive('Battle') && {W}.busy === 0", 400000, f'crown round {r}')
        await t.js("window.__tiamat.G.state.party.forEach(m => { m.moves.forEach(mv => { mv.pp = 999; }); })")
        if await t.js(f"!!{G}.state.flags.crown_champion"): break
        await t.wait(1500)
    await idle(t, 60000, 'crown done')
    print('crown:', await t.js(f"[{G}.state.flags.crown_champion, {G}.state.bag.crown_gem, {G}.state.vars.crown_round, {G}.state.vars.crown_wins, Object.keys({G}.state.defeated).filter(k => k.startsWith('elite')).join(',')]"))
    # 4) the Old Door in Rootmere
    await goto(t, 'rootmere', 18, 33, 'up')
    await t.shot('old_door_closed')
    await t.js("clearInterval(window.__auto)")
    await t.key('ArrowUp', 200, 400)
    for i in range(12):
        await t.key('z', 60, 300)
        if i == 3: await t.shot('door_gem')
        if await t.js(f"!!{G}.state.flags.ancient_door_open"): break
    await t.js(AUTO)
    await idle(t, 30000, 'door open')
    await t.shot('old_door_open')
    await t.key('ArrowUp', 200, 1200)
    await idle(t, 30000, 'tunnel')
    print('went through the door to:', await t.js(f"[{G}.state.player.map, {G}.state.player.x, {G}.state.player.y]"))
    await t.shot('tunnel_arrive')
    # 5) Keeper Enna at the carved door
    await goto(t, 'ancient_tunnel', 22, 8, 'left')
    await t.key('ArrowLeft', 200, 600)
    await wait_for(t, f"{G}.state.flags.keeper_met", 60000, 'keeper met')
    await t.wait(300)
    await t.shot('enna')
    await idle(t, 30000, 'enna done')
    await t.shot('enna_after')
    await t.js(f"{W}.player.warp(15, 6, 'up'); {G}.state.player.x = 15; {G}.state.player.y = 6")
    await t.key('ArrowUp', 200, 1200)
    await idle(t, 30000, 'cradle')
    print('inner door to:', await t.js(f"[{G}.state.player.map, {G}.state.player.x, {G}.state.player.y]"))
    await t.shot('deep_cradle')
    # 6) hatch Abzurath
    await t.js(f"{W}.player.warp(7, 5, 'up'); {G}.state.player.x = 7; {G}.state.player.y = 5")
    await t.js("clearInterval(window.__auto)")
    await t.js(f"void {W}.run('cradle.incubator')")
    for i in range(30):
        await t.key('z', 60, 350)
        if i in (3, 8): await t.shot(f'hatch_{i}')
        if await t.js(f"{G}.state.party.some(m => m.species === 'abzurath')"): break
    await t.shot('hatched')
    await t.js(AUTO)
    await idle(t, 30000, 'hatch done')
    print('abzurath:', await t.js(f"(() => {{ const m = {G}.state.party.find(m => m.species === 'abzurath') || {G}.state.boxes?.flat().find(m => m && m.species === 'abzurath'); return m ? [m.level, m.sex, m.moves.map(x => x.id).join('/'), m.ot] : null; }})()"))
    print('egg gone:', await t.js(f"!{G}.state.bag.mystery_egg"), 'flags:', await t.js(f"[{G}.state.flags.abzurath_hatched, {G}.state.index.caught.includes('abzurath')]"))


async def crownrun(t, port):
    await t.p.goto(f'http://localhost:{port}/?map=riftgate&x=33&y=11&debug')
    await wait_for(t, f"window.__tiamat && {W}.player", 40000, 'world')
    await t.wait(800)
    G = 'window.__tiamat.G'
    await t.js(f"""(() => {{ const T = window.__tiamat, G = T.G; G.settings.textSpeed = 'instant'; G.settings.battleAnims = false;
      for (const f of ['got_starter', 'mum_boots', 'cradle_done', 'crown_scene', 'game_clear', 'woke_up']) G.state.flags[f] = true;
      G.state.vars.starter = 'cindlet';
      G.state.party = ['pyromane', 'glaciursa', 'maelstrand', 'mosswarden', 'riftwyrm', 'juggernox'].map(s => T.createMon(s, 95)); }})()""")
    await t.js(AUTO)
    await goto(t, 'spire_crown', 4, 5, 'left')
    await t.js(f"{G}.state.vars.crown_round = 3")
    await goto(t, 'spire_crown', 4, 5, 'left')
    print('round reset on entry:', await t.js(f"{G}.state.vars.crown_round"))
    # talking to the wrong Warden first
    await run_script(t, 'crown.warden')
    await t.js(f"void {W}.run('crown.warden', {{ npc: {W}.npcById('crown_mossa') }})")
    seen = []
    for r in range(400):
        await t.wait(1000)
        inb = await t.js("window.__tiamat.game.scene.isActive('Battle')")
        tid = await t.js("(() => { const b = window.__tiamat.game.scene.getScene('Battle'); return b && b.trainer ? b.trainer.id : null; })()") if inb else None
        if tid and tid not in seen:
            seen.append(tid)
            await t.shot(f'crown_{tid}')
        if not inb:
            await t.js("window.__tiamat.G.state.party.forEach(m => window.__tiamat.healMon(m))")
        if await t.js(f"!!{G}.state.flags.crown_champion && {W}.busy === 0"): break
    print('battled:', seen)
    print('crown:', await t.js(f"[{G}.state.flags.crown_champion, {G}.state.bag.crown_gem, {G}.state.vars.crown_round, {G}.state.vars.crown_wins]"))
    await goto(t, 'rootmere', 18, 33, 'up')
    await t.key('ArrowUp', 200, 400)
    await wait_for(t, f"{G}.state.flags.ancient_door_open", 60000, 'door open')
    await idle(t, 30000, 'door scene')
    await t.shot('old_door_open')
    print('gem kept?', await t.js(f"{G}.state.bag.crown_gem || 0"))
    await t.key('ArrowUp', 200, 1500)
    await idle(t, 30000, 'tunnel')
    print('went through the door to:', await t.js(f"[{G}.state.player.map, {G}.state.player.x, {G}.state.player.y]"))
    await t.shot('tunnel_arrive')
    await t.key('ArrowDown', 200, 1500)
    await idle(t, 30000, 'back up')
    print('back out to:', await t.js(f"[{G}.state.player.map, {G}.state.player.x, {G}.state.player.y]"))
