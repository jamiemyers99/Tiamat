// Script registry. Each module exports an object of id → async (S, ctx) => {}
import common from './common.js';
import act1 from './act1.js';
import act2 from './act2.js';
import act3 from './act3.js';
import act4 from './act4.js';
import rescue from './rescue.js';

export const SCRIPTS = { ...common, ...act1, ...act2, ...act3, ...act4, ...rescue };
