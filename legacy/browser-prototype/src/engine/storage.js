// PC Box storage — 4 boxes × 30 slots.
// Exports: createStorage, depositMorph, withdrawMorph, findFirstOpenSlot

export const BOX_COUNT  = 4;
export const BOX_SIZE   = 30;

export function createStorage() {
  return {
    boxes: Array.from({ length: BOX_COUNT }, (_, i) => ({
      name:  `Box ${i + 1}`,
      slots: Array(BOX_SIZE).fill(null),
    })),
    activeBox: 0,
  };
}

// Returns { boxIndex, slotIndex } of the first empty slot, or null if all full.
export function findFirstOpenSlot(storage) {
  for (let b = 0; b < storage.boxes.length; b++) {
    const idx = storage.boxes[b].slots.findIndex((s) => s === null);
    if (idx !== -1) { return { boxIndex: b, slotIndex: idx }; }
  }
  return null;
}

// Deposits a creature into the first available box slot.
// Returns { boxIndex, slotIndex, boxName } on success, null if storage is full.
export function depositMorph(storage, creature) {
  const slot = findFirstOpenSlot(storage);
  if (!slot) { return null; }
  storage.boxes[slot.boxIndex].slots[slot.slotIndex] = creature;
  return { ...slot, boxName: storage.boxes[slot.boxIndex].name };
}

// Withdraws a creature from the specified box/slot.
// Returns the creature, or null if slot was empty.
export function withdrawMorph(storage, boxIndex, slotIndex) {
  const box = storage.boxes[boxIndex];
  if (!box) { return null; }
  const creature = box.slots[slotIndex];
  box.slots[slotIndex] = null;
  return creature;
}

// Swaps a party slot with a box slot (for the PC UI swap operation).
export function swapPartyWithBox(party, partyIndex, storage, boxIndex, slotIndex) {
  const box     = storage.boxes[boxIndex];
  const fromBox = box?.slots[slotIndex] ?? null;
  const fromParty = party[partyIndex] ?? null;
  if (fromBox) { party[partyIndex] = fromBox; }
  if (box)     { box.slots[slotIndex] = fromParty; }
}
