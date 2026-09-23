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
    await t.js("""(() => { const T = window.__tiamat; T.G.state.party = [T.createMon('pyromane', 74), T.createMon('glaciursa', 75, { moves: ['icicle_jab', 'hail_volley', 'power_kick', 'all_out_slam'] }), T.createMon('maelstrand', 74, { moves: ['rime_ray', 'hydro_burst', 'icicle_jab', 'undertow'] }), T.createMon('mosswarden', 72)]; })()""")
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
