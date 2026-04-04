function today() {
  return new Date();
}

function toISODate(date = today()) {
  return date.toISOString().slice(0, 10);
}

function toHumanDate(date = today()) {
  return date.toLocaleDateString('en-US', {
    weekday: 'long',
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  });
}

function hoursAgo(date, hours) {
  return Date.now() - new Date(date).getTime() < hours * 3600_000;
}

module.exports = { today, toISODate, toHumanDate, hoursAgo };
