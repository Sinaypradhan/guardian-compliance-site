const navToggle = document.querySelector('.nav-toggle');
const navLinks = document.querySelector('.nav-links');

navToggle.addEventListener('click', () => {
  const open = navLinks.classList.toggle('open');
  navToggle.classList.toggle('open', open);
  navToggle.setAttribute('aria-expanded', open);
});

navLinks.querySelectorAll('a').forEach((link) => {
  link.addEventListener('click', () => {
    navLinks.classList.remove('open');
    navToggle.classList.remove('open');
    navToggle.setAttribute('aria-expanded', 'false');
  });
});

const form = document.getElementById('contact-form');
const status = document.getElementById('form-status');

form.addEventListener('submit', (event) => {
  event.preventDefault();

  const name = document.getElementById('name').value.trim();
  const email = document.getElementById('email').value.trim();
  const message = document.getElementById('message').value.trim();

  if (!name || !email || !message) {
    showStatus('Please fill in all fields.', 'error');
    return;
  }

  if (!isValidEmail(email)) {
    showStatus('Please enter a valid email address.', 'error');
    return;
  }

  showStatus('Thanks, ' + name + '! Your message was sent (demo).', 'success');
  form.reset();
});

function isValidEmail(email) {
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
}

function showStatus(text, type) {
  status.textContent = text;
  status.className = 'form-status ' + type;
  status.hidden = false;
}
