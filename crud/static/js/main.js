const themeSelector = document.getElementById('theme-selector');

if (themeSelector) {
  // Sincronizar el valor visual del selector con el tema que ya aplicó el HEAD
  const currentTheme = document.documentElement.getAttribute('data-bs-theme') || 'light';
  themeSelector.value = currentTheme;

  // Escuchar cuando el usuario cambia la opción manualmente
  themeSelector.addEventListener('change', (e) => {
    const selectedTheme = e.target.value;
    document.documentElement.setAttribute('data-bs-theme', selectedTheme);
    localStorage.setItem('theme', selectedTheme);
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