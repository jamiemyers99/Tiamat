export function beginDialogue(state, speaker, lines) {
  state.activeDialogue = {
    speaker,
    lines,
    lineIndex: 0,
    visibleChars: 0,
    timer: 0,
    finished: false,
  };
}

const CHAR_SPEEDS = { slow: 60, normal: 24, fast: 8 };

export function updateDialogue(state, input, delta) {
  const dialogue = state.activeDialogue;
  if (!dialogue) {
    return false;
  }

  const line = dialogue.lines[dialogue.lineIndex];
  const msPerChar = CHAR_SPEEDS[state.settings?.textSpeed] ?? 24;
  dialogue.timer += delta;
  while (dialogue.timer >= msPerChar && dialogue.visibleChars < line.length) {
    dialogue.timer -= msPerChar;
    dialogue.visibleChars += 1;
  }

  if (dialogue.visibleChars >= line.length) {
    dialogue.finished = true;
  }

  if (input.wasPressed("e", " ", "enter")) {
    if (!dialogue.finished) {
      dialogue.visibleChars = line.length;
      dialogue.finished = true;
      return true;
    }

    if (dialogue.lineIndex < dialogue.lines.length - 1) {
      dialogue.lineIndex += 1;
      dialogue.visibleChars = 0;
      dialogue.timer = 0;
      dialogue.finished = false;
      return true;
    }

    state.activeDialogue = null;
    return true;
  }

  return false;
}

export function getDialogueLine(dialogue) {
  return dialogue.lines[dialogue.lineIndex].slice(0, dialogue.visibleChars);
}
