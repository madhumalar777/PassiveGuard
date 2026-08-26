interface Telemetry {
  interaction_duration: number;
  mouse_count: number;
  mouse_speed_mean: number;
  mouse_speed_variance: number;
  click_count: number;
  click_interval_variance: number;
  scroll_count: number;
  keyboard_count: number;
  request_frequency: number;
  webdriver_flag: number;
  touch_support: number;
  viewport_width: number;
  viewport_height: number;
  timezone_offset: number;
  hardware_concurrency: number;
}

let mousePositions: [number, number][] = [];
let clickTimes: number[] = [];
let scrollTimes: number[] = [];
let keyboardTimes: number[] = [];
const startTime = Date.now();

export function initTelemetryCollection() {
  // Track mouse movement
  document.addEventListener('mousemove', (e) => {
    mousePositions.push([e.clientX, e.clientY]);
    if (mousePositions.length > 1000) mousePositions.shift();
  });

  // Track clicks
  document.addEventListener('click', () => {
    clickTimes.push(Date.now());
  });

  // Track scrolls
  document.addEventListener('scroll', () => {
    scrollTimes.push(Date.now());
  });

  // Track keyboard
  document.addEventListener('keydown', () => {
    keyboardTimes.push(Date.now());
  });
}

function calculateMouseStats() {
  if (mousePositions.length < 2) {
    return { speed_mean: 0, speed_variance: 0 };
  }

  const speeds: number[] = [];
  for (let i = 1; i < mousePositions.length; i++) {
    const dx = mousePositions[i][0] - mousePositions[i - 1][0];
    const dy = mousePositions[i][1] - mousePositions[i - 1][1];
    const distance = Math.sqrt(dx * dx + dy * dy);
    speeds.push(distance);
  }

  const mean = speeds.reduce((a, b) => a + b, 0) / speeds.length;
  const variance = speeds.reduce((sum, speed) => sum + Math.pow(speed - mean, 2), 0) / speeds.length;

  return {
    speed_mean: Math.min(mean, 20),
    speed_variance: Math.min(variance, 5),
  };
}

function calculateClickIntervals() {
  if (clickTimes.length < 2) {
    return 0;
  }

  const intervals: number[] = [];
  for (let i = 1; i < clickTimes.length; i++) {
    intervals.push(clickTimes[i] - clickTimes[i - 1]);
  }

  const mean = intervals.reduce((a, b) => a + b, 0) / intervals.length;
  const variance = intervals.reduce((sum, interval) => sum + Math.pow(interval - mean, 2), 0) / intervals.length;

  return Math.sqrt(variance) / 1000; // Convert to seconds
}

export function collectTelemetry(): Telemetry {
  const now = Date.now();
  const interactionDuration = (now - startTime) / 1000;

  const mouseStats = calculateMouseStats();
  const clickIntervalVar = calculateClickIntervals();

  const uniqueScrollTimes = new Set(scrollTimes.map((t) => Math.floor(t / 100)));
  const uniqueKeyTimes = new Set(keyboardTimes.map((t) => Math.floor(t / 100)));

  const telemetry: Telemetry = {
    interaction_duration: parseFloat(interactionDuration.toFixed(2)),
    mouse_count: mousePositions.length,
    mouse_speed_mean: parseFloat(mouseStats.speed_mean.toFixed(2)),
    mouse_speed_variance: parseFloat(mouseStats.speed_variance.toFixed(2)),
    click_count: clickTimes.length,
    click_interval_variance: parseFloat(clickIntervalVar.toFixed(2)),
    scroll_count: uniqueScrollTimes.size,
    keyboard_count: uniqueKeyTimes.size,
    request_frequency: 1.0,
    webdriver_flag: navigator.webdriver ? 1 : 0,
    touch_support: 'ontouchstart' in window ? 1 : 0,
    viewport_width: window.innerWidth,
    viewport_height: window.innerHeight,
    timezone_offset: new Date().getTimezoneOffset(),
    hardware_concurrency: navigator.hardwareConcurrency || 4,
  };

  // Reset for next collection
  mousePositions = [];
  clickTimes = [];
  scrollTimes = [];
  keyboardTimes = [];

  return telemetry;
}