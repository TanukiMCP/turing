/* Table Ready behaviour. The pages work without this file: every player
   count is listed. This script narrows a game page to the chosen count,
   remembers setup ticks, and filters the game list on the home page. */
(function () {
  "use strict";

  var PLAYERS_KEY = "tableready.players";

  function read(key) {
    try { return window.localStorage.getItem(key); } catch (err) { return null; }
  }
  function write(key, value) {
    try {
      if (value === null) { window.localStorage.removeItem(key); } else { window.localStorage.setItem(key, value); }
    } catch (err) { /* storage unavailable: the page still works for this visit */ }
  }
  function each(root, selector, fn) {
    Array.prototype.forEach.call(root.querySelectorAll(selector), fn);
  }
  function plural(n) { return n === 1 ? "1 player" : n + " players"; }

  each(document, ".js-only", function (el) { el.hidden = false; });

  /* ---------- Game page ---------- */
  var game = document.querySelector("main.game");
  if (game) {
    var min = Number(game.dataset.min);
    var max = Number(game.dataset.max);
    var covered = game.dataset.covered.split(",").map(Number);
    var help = game.querySelector(".count-help");
    var radios = game.querySelectorAll('input[name="players"]');
    var motionOk = !window.matchMedia || !window.matchMedia("(prefers-reduced-motion: reduce)").matches;

    var applyCount = function (count, announce) {
      each(game, ".per[data-count], .variant[data-count]", function (el) {
        var match = count !== null && Number(el.dataset.count) === count;
        el.hidden = count !== null && !match;
        el.classList.toggle("is-chosen", match);
        if (match && announce && motionOk) {
          el.classList.remove("just-changed");
          void el.offsetWidth; /* restart the highlight */
          el.classList.add("just-changed");
        }
      });
      each(game, "[data-only]", function (el) {
        var only = el.dataset.only.split(",").map(Number);
        el.hidden = count !== null && only.indexOf(count) === -1;
        var label = el.querySelector(".only-label");
        if (label) { label.hidden = count !== null; }
      });
      Array.prototype.forEach.call(radios, function (radio) {
        radio.checked = count === null ? radio.value === "" : Number(radio.value) === count && radio.value !== "";
      });
      if (announce) {
        help.textContent = count === null
          ? "Showing every player count. Pick yours to see only what applies."
          : "Showing " + plural(count) + ".";
      }
    };

    var urlCount = new URLSearchParams(window.location.search).get("players");
    var stored = urlCount !== null ? urlCount : read(PLAYERS_KEY);
    var wanted = stored === null || stored === "" ? null : Number(stored);
    if (wanted !== null && covered.indexOf(wanted) !== -1) {
      applyCount(wanted, false);
      help.textContent = "Showing " + plural(wanted) + ".";
    } else {
      applyCount(null, false);
      if (wanted !== null && !isNaN(wanted)) {
        var why = wanted < min || wanted > max
          ? "This game takes " + (min === max ? plural(min) : min + "–" + max + " players")
          : (wanted === 1 ? "Solo play isn't covered yet" : "That count isn't covered yet");
        help.textContent = "You last chose " + plural(wanted) + ". " + why + ", so every count is shown.";
      } else {
        help.textContent = "Showing every player count. Pick yours to see only what applies.";
      }
    }

    Array.prototype.forEach.call(radios, function (radio) {
      radio.addEventListener("change", function () {
        var count = radio.value === "" ? null : Number(radio.value);
        applyCount(count, true);
        write(PLAYERS_KEY, count === null ? null : String(count));
        var url = new URL(window.location.href);
        if (count === null) { url.searchParams.delete("players"); } else { url.searchParams.set("players", String(count)); }
        try { window.history.replaceState(null, "", url); } catch (err) { /* file:// in some browsers */ }
      });
    });

    /* Setup ticks, remembered per game on this device. */
    var ticksKey = "tableready.ticks." + game.dataset.slug;
    var boxes = game.querySelectorAll(".step input[type=checkbox]");
    var clear = game.querySelector(".clear-ticks");
    var saved = [];
    try { saved = JSON.parse(read(ticksKey) || "[]"); } catch (err) { saved = []; }
    var syncClear = function () {
      var any = Array.prototype.some.call(boxes, function (box) { return box.checked; });
      clear.hidden = !any;
    };
    Array.prototype.forEach.call(boxes, function (box) {
      box.checked = saved.indexOf(Number(box.dataset.step)) !== -1;
      box.addEventListener("change", function () {
        var ticked = Array.prototype.filter.call(boxes, function (b) { return b.checked; })
          .map(function (b) { return Number(b.dataset.step); });
        write(ticksKey, ticked.length ? JSON.stringify(ticked) : null);
        syncClear();
      });
    });
    syncClear();
    clear.addEventListener("click", function () {
      Array.prototype.forEach.call(boxes, function (box) { box.checked = false; });
      write(ticksKey, null);
      syncClear();
      var heading = game.querySelector("#setup h2");
      heading.setAttribute("tabindex", "-1");
      heading.focus();
    });
  }

  /* ---------- Home page ---------- */
  var find = document.getElementById("find");
  if (find) {
    var rows = document.querySelectorAll(".game-row");
    var list = document.querySelector(".game-list");
    var noMatch = document.querySelector(".no-match");
    var term = document.querySelector(".no-match-term");
    var fold = function (text) {
      return text.toLowerCase().normalize("NFD").replace(/[̀-ͯ]/g, "").trim();
    };
    var filter = function () {
      var query = fold(find.value);
      var shown = 0;
      Array.prototype.forEach.call(rows, function (row) {
        var hit = query === "" || fold(row.dataset.name).indexOf(query) !== -1;
        row.hidden = !hit;
        if (hit) { shown += 1; }
      });
      list.hidden = shown === 0;
      noMatch.hidden = shown !== 0;
      term.textContent = find.value.trim();
    };
    find.addEventListener("input", filter);
    document.querySelector(".clear-search").addEventListener("click", function () {
      find.value = "";
      filter();
      find.focus();
    });
    filter();
  }
})();
