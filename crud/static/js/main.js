const themeSelector = document.getElementById('theme-selector');

if (themeSelector) {
  const currentTheme = document.documentElement.getAttribute('data-bs-theme') || 'light';
  themeSelector.value = currentTheme;
  const userId = themeSelector.getAttribute('data-user');

  themeSelector.addEventListener('change', (e) => {
    const selectedTheme = e.target.value;
    document.documentElement.setAttribute('data-bs-theme', selectedTheme);
    localStorage.setItem('theme_' + userId, selectedTheme);
  });
}

const btnDelete = document.querySelectorAll('.btn-borrar');
if(btnDelete) {
  const btnArray = Array.from(btnDelete);
  btnArray.forEach((btn) => {
    btn.addEventListener('click', (e) => {
      if(!confirm('¿Está seguro de querer borrar?')){
        e.preventDefault();
      }
    });
  });
}