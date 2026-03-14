(() => {
  // ── password visibility toggle ─────────────────────────────────────────────
  document.querySelectorAll(".toggle-pw").forEach(btn => {
    btn.addEventListener("click", () => {
      const input = btn.previousElementSibling;
      input.type  = input.type === "password" ? "text" : "password";
      btn.textContent = input.type === "password" ? "👁" : "🙈";
    });
  });

  // ── password strength meter ────────────────────────────────────────────────
  const pwInput = document.getElementById("password");
  const fill    = document.getElementById("strengthFill");
  const label   = document.getElementById("strengthLabel");

  if (pwInput && fill) {
    pwInput.addEventListener("input", () => {
      const val    = pwInput.value;
      let score    = 0;

      if (val.length >= 8)                     score++;
      if (val.length >= 12)                    score++;
      if (/[A-Z]/.test(val))                   score++;
      if (/[0-9]/.test(val))                   score++;
      if (/[^A-Za-z0-9]/.test(val))            score++;

      const levels = [
        { pct: "0%",   color: "transparent",  text: "Password strength" },
        { pct: "25%",  color: "#ff5252",       text: "Weak" },
        { pct: "50%",  color: "#ffb74d",       text: "Fair" },
        { pct: "75%",  color: "#fff176",       text: "Good" },
        { pct: "100%", color: "#00ff88",       text: "Strong" },
      ];

      const lvl          = levels[Math.min(score, 4)];
      fill.style.width   = lvl.pct;
      fill.style.background = lvl.color;
      if (label) label.textContent = lvl.text;
    });
  }

  // ── OTP input — numbers only, auto-submit on 6 digits ─────────────────────
  const otpInput = document.getElementById("otp");
  const otpForm  = document.getElementById("otpForm");

  if (otpInput) {
    otpInput.addEventListener("input", () => {
      otpInput.value = otpInput.value.replace(/\D/g, "").slice(0, 6);
      if (otpInput.value.length === 6 && otpForm) otpForm.submit();
    });

    otpInput.focus();
  }
})();
