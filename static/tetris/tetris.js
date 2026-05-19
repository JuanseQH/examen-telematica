/**
 * Tetris web — Examen 3 Telemática
 * Adaptación a JavaScript/Canvas de un Tetris propio (lógica de tablero, piezas y temas).
 */
(function () {
  'use strict';

  // --- Constantes de tablero, piezas y temas visuales ---

  const GRID_W = 10;
  const GRID_H = 20;
  const CELL = 30;
  const BLACK = '#000000';

  const SHAPES = {
    I: [[1, 1, 1, 1]],
    O: [[1, 1], [1, 1]],
    T: [[0, 1, 0], [1, 1, 1]],
    S: [[0, 1, 1], [1, 1, 0]],
    Z: [[1, 1, 0], [0, 1, 1]],
    J: [[1, 0, 0], [1, 1, 1]],
    L: [[0, 0, 1], [1, 1, 1]],
  };

  const SHAPE_COLORS = {
    I: '#00ffff',
    O: '#ffff00',
    T: '#800080',
    S: '#00ff00',
    Z: '#ff0000',
    J: '#0000ff',
    L: '#ffa500',
  };

  const THEMES = {
    clasico: {
      background: '#808080',
      grid: '#ffffff',
      piece_colors: { ...SHAPE_COLORS },
      ghost: 'rgba(120, 220, 255, 0.45)',
    },
    oscuro: {
      background: '#1e1e1e',
      grid: '#505050',
      piece_colors: {
        I: '#00ffff', O: '#ffff64', T: '#c800c8', S: '#00ff64',
        Z: '#ff5050', J: '#5050ff', L: '#ffb450',
      },
      ghost: 'rgba(80, 180, 255, 0.4)',
    },
    neon: {
      background: '#0a0a1e',
      grid: '#00ffff',
      piece_colors: {
        I: '#00ffff', O: '#ffff00', T: '#ff00ff', S: '#00ff00',
        Z: '#ff0000', J: '#0000ff', L: '#ff8000',
      },
      ghost: 'rgba(255, 255, 255, 0.35)',
    },
    retro: {
      background: '#f5deb3',
      grid: '#8b4513',
      piece_colors: {
        I: '#008080', O: '#ffd700', T: '#800080', S: '#556b2f',
        Z: '#b22222', J: '#191970', L: '#d2691e',
      },
      ghost: 'rgba(139, 69, 19, 0.4)',
    },
  };

  const THEME_LIST = Object.keys(THEMES);
  const SCORE_TABLE = [0, 40, 100, 300, 1200];
  const HS_KEY = 'examen_tetris_highscore';
  const THEME_KEY = 'examen_tetris_theme';

  function cloneGrid() {
    return Array.from({ length: GRID_H }, () => Array(GRID_W).fill(BLACK));
  }

  function rotateMatrix(matrix) {
    const rows = matrix.length;
    const cols = matrix[0].length;
    const out = Array.from({ length: cols }, () => Array(rows).fill(0));
    for (let r = 0; r < rows; r++) {
      for (let c = 0; c < cols; c++) {
        out[c][rows - 1 - r] = matrix[r][c];
      }
    }
    return out;
  }

  function randomShapeName() {
    const keys = Object.keys(SHAPES);
    return keys[(Math.random() * keys.length) | 0];
  }

  // --- Pieza activa: forma, posición y rotación ---
  class Piece {
    constructor(shapeName) {
      this.shapeName = shapeName || randomShapeName();
      this.shape = SHAPES[this.shapeName].map((row) => [...row]);
      this.rotation = 0;
      this.x = (GRID_W / 2) | 0;
      this.x -= (this.shape[0].length / 2) | 0;
      this.y = 0;
    }

    color(theme) {
      const t = theme || window.__tetrisTheme;
      return t ? t.piece_colors[this.shapeName] : SHAPE_COLORS[this.shapeName];
    }

    clone() {
      const p = new Piece(this.shapeName);
      p.shape = this.shape.map((row) => [...row]);
      p.rotation = this.rotation;
      p.x = this.x;
      p.y = this.y;
      return p;
    }
  }

  // --- Tablero: colisiones, bloqueo de piezas y limpieza de líneas ---
  class Board {
    constructor() {
      this.grid = cloneGrid();
      this.linesToClear = [];
      this.clearAnimFrame = 0;
    }

    isValid(piece, x, y) {
      for (let r = 0; r < piece.shape.length; r++) {
        for (let c = 0; c < piece.shape[r].length; c++) {
          if (!piece.shape[r][c]) continue;
          const gx = x + c;
          const gy = y + r;
          if (gx < 0 || gx >= GRID_W || gy >= GRID_H) return false;
          if (gy >= 0 && this.grid[gy][gx] !== BLACK) return false;
        }
      }
      return true;
    }

    lockPiece(piece, theme) {
      const color = piece.color(theme);
      for (let r = 0; r < piece.shape.length; r++) {
        for (let c = 0; c < piece.shape[r].length; c++) {
          if (piece.shape[r][c]) {
            const gy = piece.y + r;
            const gx = piece.x + c;
            if (gy >= 0) this.grid[gy][gx] = color;
          }
        }
      }
    }

    checkLinesToClear() {
      this.linesToClear = [];
      for (let y = 0; y < GRID_H; y++) {
        if (this.grid[y].every((cell) => cell !== BLACK)) {
          this.linesToClear.push(y);
        }
      }
      return this.linesToClear.length;
    }

    animateClearStep() {
      const flash = this.clearAnimFrame % 2 === 0 ? '#c8c8c8' : BLACK;
      for (const row of this.linesToClear) {
        for (let x = 0; x < GRID_W; x++) this.grid[row][x] = flash;
      }
      this.clearAnimFrame++;
    }

    clearLines() {
      if (!this.linesToClear.length) return 0;
      const skip = new Set(this.linesToClear);
      const kept = this.grid.filter((_, idx) => !skip.has(idx));
      const n = this.linesToClear.length;
      for (let i = 0; i < n; i++) {
        kept.unshift(Array(GRID_W).fill(BLACK));
      }
      this.grid = kept;
      this.linesToClear = [];
      this.clearAnimFrame = 0;
      return n;
    }

    clearTopHalf() {
      const half = (GRID_H / 2) | 0;
      for (let y = 0; y < half; y++) {
        for (let x = 0; x < GRID_W; x++) this.grid[y][x] = BLACK;
      }
    }
  }

  // --- Bucle principal, entrada de teclado, puntuación y dibujado en canvas ---
  class TetrisGame {
    constructor(mainCanvas, nextCanvas, holdCanvas, ui) {
      this.canvas = mainCanvas;
      this.ctx = mainCanvas.getContext('2d');
      this.nextCtx = nextCanvas.getContext('2d');
      this.holdCtx = holdCanvas.getContext('2d');
      this.ui = ui;

      this.themeName = localStorage.getItem(THEME_KEY) || 'neon';
      this.gameMode = 0;
      this.state = 'menu';
      this.board = new Board();
      this.current = null;
      this.next = null;
      this.held = null;
      this.canHold = true;
      this.score = 0;
      this.lines = 0;
      this.level = 1;
      this.highScore = parseInt(localStorage.getItem(HS_KEY) || '0', 10);
      this.fallAccumulator = 0;
      this.fallSpeed = 0.8;
      this.baseFallSpeed = 0.8;
      this.startTime = 0;
      this.lastTs = 0;
      this.clearing = false;
      this.keys = {};
      this.das = { left: 0, right: 0, down: 0 };

      this._bindInputs();
      this._syncThemeButtons();
      this._syncModeButtons();
      this.showOverlay('menu');
      this._updateStats();
      requestAnimationFrame((t) => this.loop(t));
    }

    get theme() {
      return THEMES[this.themeName];
    }

    setTheme(name) {
      if (!THEMES[name]) return;
      this.themeName = name;
      localStorage.setItem(THEME_KEY, name);
      window.__tetrisTheme = this.theme;
      this._syncThemeButtons();
    }

    _syncThemeButtons() {
      this.ui.themeBtns.forEach((btn) => {
        btn.classList.toggle('active', btn.dataset.theme === this.themeName);
      });
    }

    _syncModeButtons() {
      this.ui.modeBtns.forEach((btn, i) => {
        btn.classList.toggle('active', i === this.gameMode);
      });
    }

    _bindInputs() {
      document.addEventListener('keydown', (e) => {
        if (['ArrowLeft', 'ArrowRight', 'ArrowDown', 'ArrowUp', ' ', 'c', 'C', 'p', 'P', 'Escape', 'Enter', 'Tab'].includes(e.key)) {
          e.preventDefault();
        }
        this.keys[e.key] = true;

        if (this.state === 'menu') {
          if (e.key === 'Enter' || e.code === 'NumpadEnter') this.startGame();
          if (e.key === 'Tab') {
            this.gameMode = (this.gameMode + 1) % 3;
            this._syncModeButtons();
          }
          return;
        }
        if (this.state === 'gameover') {
          if (e.key === 'Enter') this.startGame();
          if (e.key === 'm' || e.key === 'M') this.state = 'menu';
          return;
        }
        if (this.state === 'paused') {
          if (e.key === 'p' || e.key === 'P' || e.key === 'Escape') {
            this.state = 'playing';
            this.ui.overlay.classList.add('hidden');
          }
          return;
        }
        if (this.state !== 'playing') return;

        if (e.key === 'p' || e.key === 'P' || e.key === 'Escape') {
          this.state = 'paused';
          this.ui.overlayTitle.textContent = 'Pausa';
          this.ui.overlayText.textContent = 'P o Esc para continuar';
          this.ui.overlayBtn.classList.add('hidden');
          this.ui.overlay.classList.remove('hidden');
        }
        if (e.key === 'ArrowUp') this.rotate();
        if (e.key === ' ') this.hardDrop();
        if (e.key === 'c' || e.key === 'C') this.hold();
      });

      document.addEventListener('keyup', (e) => {
        this.keys[e.key] = false;
        if (['ArrowLeft', 'ArrowRight', 'ArrowDown'].includes(e.key)) {
          this.das[e.key === 'ArrowLeft' ? 'left' : e.key === 'ArrowRight' ? 'right' : 'down'] = 0;
        }
      });

      this.ui.overlayBtn.addEventListener('click', (e) => {
        e.preventDefault();
        e.stopPropagation();
        if (this.state === 'menu' || this.state === 'gameover') this.startGame();
      });

      this.ui.themeBtns.forEach((btn) => {
        btn.addEventListener('click', () => this.setTheme(btn.dataset.theme));
      });

      this.ui.modeBtns.forEach((btn, i) => {
        btn.addEventListener('click', () => {
          this.gameMode = i;
          this._syncModeButtons();
        });
      });
    }

    showOverlay(kind) {
      const o = this.ui.overlay;
      o.classList.remove('hidden');
      this.ui.overlayBtn.classList.remove('hidden');
      if (kind === 'menu') {
        this.ui.overlayTitle.textContent = 'TETRIS';
        this.ui.overlayText.textContent = 'Enter o clic en Jugar · Tab cambia modo';
        this.ui.overlayBtn.textContent = 'Jugar';
        this.state = 'menu';
      } else if (kind === 'gameover') {
        this.ui.overlayTitle.textContent = 'Game Over';
        this.ui.overlayText.textContent = `Puntuación: ${this.score} · Enter para reintentar`;
        this.ui.overlayBtn.textContent = 'Reintentar';
        this.state = 'gameover';
      }
    }

    resetGame() {
      this.board = new Board();
      this.current = new Piece();
      this.next = new Piece();
      this.held = null;
      this.canHold = true;
      this.score = 0;
      this.lines = 0;
      this.level = 1;
      this.fallAccumulator = 0;
      this.fallSpeed = 0.8;
      this.baseFallSpeed = 0.8;
      this.startTime = performance.now();
      this.clearing = false;
      window.__tetrisTheme = this.theme;
    }

    startGame() {
      this.resetGame();
      this.state = 'playing';
      this.lastTs = 0;
      this.fallAccumulator = 0;
      this.ui.overlay.classList.add('hidden');
      this.ui.overlayBtn.classList.remove('hidden');
      this._updateStats();
    }

    loop(ts) {
      if (!this.lastTs) this.lastTs = ts;
      const dt = Math.min(0.05, (ts - this.lastTs) / 1000);
      this.lastTs = ts;

      if (this.state === 'playing') {
        this.update(dt);
      }
      this.draw();
      requestAnimationFrame((t) => this.loop(t));
    }

    updateSpeed() {
      const elapsed = (performance.now() - this.startTime) / 1000;
      const timeFactor = Math.min(0.6, elapsed / 60);
      const levelFactor = Math.min(0.4, (this.level - 1) * 0.05);
      this.fallSpeed = Math.max(0.1, this.baseFallSpeed - timeFactor - levelFactor);
    }

    update(dt) {
      if (this.clearing) {
        if (this.board.clearAnimFrame < 6) {
          this.board.animateClearStep();
          return;
        }
        const cleared = this.board.clearLines();
        if (cleared > 0) {
          this.lines += cleared;
          if (this.gameMode !== 2) {
            this.score += SCORE_TABLE[cleared] * this.level;
            this.level = ((this.lines / 10) | 0) + 1;
          }
        }
        this.clearing = false;
        this.fallAccumulator = 0;
      }

      this.updateSpeed();
      this._handleMovement(dt);

      if (!this.clearing) {
        this.fallAccumulator += dt;
        if (this.fallAccumulator >= this.fallSpeed) {
          this.fallAccumulator = 0;
          this.softDrop();
        }
      }

      this._updateStats();
    }

    _handleMovement(dt) {
      const repeat = 0.12;
      const initial = 0.18;
      if (this.keys.ArrowLeft) {
        this.das.left += dt;
        if (this.das.left === dt || this.das.left > initial && (this.das.left - initial) % repeat < dt) {
          this.move(-1, 0);
        }
      }
      if (this.keys.ArrowRight) {
        this.das.right += dt;
        if (this.das.right === dt || this.das.right > initial && (this.das.right - initial) % repeat < dt) {
          this.move(1, 0);
        }
      }
      if (this.keys.ArrowDown) {
        this.das.down += dt;
        if (this.das.down === dt || this.das.down > initial && (this.das.down - initial) % repeat < dt) {
          this.softDrop();
          this.fallAccumulator = 0;
        }
      }
    }

    move(dx, dy) {
      if (this.board.isValid(this.current, this.current.x + dx, this.current.y + dy)) {
        this.current.x += dx;
        this.current.y += dy;
        return true;
      }
      return false;
    }

    softDrop() {
      if (this.move(0, 1)) return;
      this.lockAndSpawn();
    }

    hardDrop() {
      while (this.move(0, 1)) { /* drop */ }
      this.lockAndSpawn();
    }

    rotate() {
      const temp = this.current.clone();
      temp.shape = rotateMatrix(temp.shape);
      temp.rotation = (temp.rotation + 1) % 4;
      if (this.board.isValid(temp, temp.x, temp.y)) {
        this.current.shape = temp.shape;
        this.current.rotation = temp.rotation;
        return;
      }
      if (this.board.isValid(temp, temp.x - 1, temp.y)) {
        this.current.x--;
        this.current.shape = temp.shape;
        this.current.rotation = temp.rotation;
      } else if (this.board.isValid(temp, temp.x + 1, temp.y)) {
        this.current.x++;
        this.current.shape = temp.shape;
        this.current.rotation = temp.rotation;
      }
    }

    hold() {
      if (!this.canHold) return;
      if (!this.held) {
        this.held = new Piece(this.current.shapeName);
        this.current = this.next;
        this.next = new Piece();
      } else {
        const tmp = this.held;
        this.held = new Piece(this.current.shapeName);
        this.current = tmp;
        this.current.x = (GRID_W / 2) | 0;
        this.current.x -= (this.current.shape[0].length / 2) | 0;
        this.current.y = 0;
      }
      if (!this.board.isValid(this.current, this.current.x, this.current.y)) {
        const tmp = this.held;
        this.held = new Piece(this.current.shapeName);
        this.current = tmp;
        return;
      }
      this.canHold = false;
    }

    lockAndSpawn() {
      this.board.lockPiece(this.current, this.theme);
      const pendingClear = this.board.checkLinesToClear() > 0;
      this.spawnNext();
      if (pendingClear) {
        this.clearing = true;
        this.board.clearAnimFrame = 0;
      }
    }

    resetPieceSpawn(piece) {
      piece.x = (GRID_W / 2) | 0;
      piece.x -= (piece.shape[0].length / 2) | 0;
      piece.y = 0;
    }

    spawnNext() {
      this.current = this.next;
      this.next = new Piece();
      this.resetPieceSpawn(this.current);
      this.canHold = true;

      if (this.gameMode === 2 && !this.board.isValid(this.current, this.current.x, this.current.y)) {
        this.board.clearTopHalf();
      } else if (this.gameMode !== 2 && !this.board.isValid(this.current, this.current.x, this.current.y)) {
        if (this.score > this.highScore) {
          this.highScore = this.score;
          localStorage.setItem(HS_KEY, String(this.highScore));
        }
        this.showOverlay('gameover');
        return;
      }
    }

    ghostY() {
      let y = this.current.y;
      while (this.board.isValid(this.current, this.current.x, y + 1)) y++;
      return y;
    }

    _updateStats() {
      if (this.state !== 'playing' || !this.startTime) return;
      const elapsed = ((performance.now() - this.startTime) / 1000) | 0;
      const mm = String((elapsed / 60) | 0).padStart(2, '0');
      const ss = String(elapsed % 60).padStart(2, '0');
      this.ui.score.textContent = this.gameMode === 2 ? '—' : String(this.score);
      this.ui.lines.textContent = String(this.lines);
      this.ui.level.textContent = this.gameMode === 2 ? 'Zen' : String(this.level);
      this.ui.time.textContent = `${mm}:${ss}`;
      this.ui.high.textContent = String(this.highScore);
      const modes = ['Clásico', 'Maratón', 'Zen'];
      this.ui.modeLabel.textContent = modes[this.gameMode];
    }

    drawMini(ctx, piece) {
      const w = 4 * CELL;
      const h = 4 * CELL;
      ctx.canvas.width = w;
      ctx.canvas.height = h;
      ctx.fillStyle = 'rgba(0,0,0,0.35)';
      ctx.fillRect(0, 0, w, h);
      if (!piece) return;
      const shape = piece.shape;
      const offX = ((4 - shape[0].length) / 2) * CELL;
      const offY = ((4 - shape.length) / 2) * CELL;
      for (let r = 0; r < shape.length; r++) {
        for (let c = 0; c < shape[r].length; c++) {
          if (shape[r][c]) {
            ctx.fillStyle = this.theme.piece_colors[piece.shapeName];
            ctx.fillRect(offX + c * CELL, offY + r * CELL, CELL - 2, CELL - 2);
          }
        }
      }
    }

    draw() {
      window.__tetrisTheme = this.theme;
      const { ctx, canvas } = this;
      ctx.fillStyle = '#000';
      ctx.fillRect(0, 0, canvas.width, canvas.height);

      const gridColor = this.theme.grid;

      for (let y = 0; y < GRID_H; y++) {
        for (let x = 0; x < GRID_W; x++) {
          const color = this.board.grid[y][x];
          const px = x * CELL;
          const py = y * CELL;
          ctx.fillStyle = color;
          ctx.fillRect(px, py, CELL, CELL);
          if (color === BLACK) {
            ctx.strokeStyle = gridColor;
            ctx.lineWidth = 1;
            ctx.strokeRect(px + 0.5, py + 0.5, CELL - 1, CELL - 1);
          }
        }
      }

      if (this.state === 'playing' && this.current) {
        const gy = this.ghostY();
        this._drawPiece(this.current, this.current.x, gy, true);

        for (let r = 0; r < this.current.shape.length; r++) {
          for (let c = 0; c < this.current.shape[r].length; c++) {
            if (!this.current.shape[r][c]) continue;
            const px = (this.current.x + c) * CELL;
            const py = (this.current.y + r) * CELL;
            ctx.fillStyle = this.theme.piece_colors[this.current.shapeName];
            ctx.fillRect(px, py, CELL, CELL);
            ctx.strokeStyle = '#fff';
            ctx.lineWidth = 2;
            ctx.strokeRect(px + 1, py + 1, CELL - 2, CELL - 2);
          }
        }
      }

      this.drawMini(this.nextCtx, this.next);
      this.drawMini(this.holdCtx, this.held);
    }

    _drawPiece(piece, x, y, ghost) {
      const ctx = this.ctx;
      for (let r = 0; r < piece.shape.length; r++) {
        for (let c = 0; c < piece.shape[r].length; c++) {
          if (!piece.shape[r][c]) continue;
          const px = (x + c) * CELL;
          const py = (y + r) * CELL;
          if (ghost) {
            ctx.fillStyle = this.theme.ghost;
            ctx.fillRect(px + 2, py + 2, CELL - 4, CELL - 4);
          }
        }
      }
    }
  }

  // --- Inicialización al cargar la página (DOM listo) ---
  function init() {
    const main = document.getElementById('tetris-canvas');
    const next = document.getElementById('next-canvas');
    const hold = document.getElementById('hold-canvas');
    if (!main) return;

    main.width = GRID_W * CELL;
    main.height = GRID_H * CELL;

    const ui = {
      overlay: document.getElementById('tetris-overlay'),
      overlayTitle: document.getElementById('overlay-title'),
      overlayText: document.getElementById('overlay-text'),
      overlayBtn: document.getElementById('overlay-btn'),
      score: document.getElementById('stat-score'),
      lines: document.getElementById('stat-lines'),
      level: document.getElementById('stat-level'),
      time: document.getElementById('stat-time'),
      high: document.getElementById('stat-high'),
      modeLabel: document.getElementById('stat-mode'),
      themeBtns: document.querySelectorAll('.theme-btn'),
      modeBtns: document.querySelectorAll('.mode-btn'),
    };

    window.__tetrisTheme = THEMES.neon;

    try {
      new TetrisGame(main, next, hold, ui);
    } catch (err) {
      console.error('No se pudo iniciar Tetris:', err);
      const overlay = document.getElementById('tetris-overlay');
      if (overlay) {
        overlay.classList.remove('hidden');
        const title = document.getElementById('overlay-title');
        const text = document.getElementById('overlay-text');
        if (title) title.textContent = 'Error al cargar';
        if (text) text.textContent = String(err.message || err);
      }
    }
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
