const LEVELS = { debug: 0, info: 1, warn: 2, error: 3 };
const THRESHOLD = LEVELS[process.env.LOG_LEVEL] ?? LEVELS.info;

const COLORS = {
  debug: '\x1b[90m',
  info: '\x1b[36m',
  warn: '\x1b[33m',
  error: '\x1b[31m',
  reset: '\x1b[0m',
};

function fmt(level, msg, meta) {
  const ts = new Date().toISOString();
  const tag = `${COLORS[level]}[${level.toUpperCase()}]${COLORS.reset}`;
  const base = `${ts} ${tag} ${msg}`;
  return meta !== undefined ? `${base} ${JSON.stringify(meta)}` : base;
}

const logger = {};

for (const level of Object.keys(LEVELS)) {
  logger[level] = (msg, meta) => {
    if (LEVELS[level] >= THRESHOLD) {
      const stream = level === 'error' ? process.stderr : process.stdout;
      stream.write(fmt(level, msg, meta) + '\n');
    }
  };
}

logger.child = (prefix) => {
  const child = {};
  for (const level of Object.keys(LEVELS)) {
    child[level] = (msg, meta) => logger[level](`[${prefix}] ${msg}`, meta);
  }
  child.child = (sub) => logger.child(`${prefix}:${sub}`);
  return child;
};

module.exports = logger;
