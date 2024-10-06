/* script.js */
const maleAvatarUpload = document.querySelector('#maleAvatar');
const maleAvatarPreview = document.querySelector('#malePreview');

const femaleAvatarUpload = document.querySelector('#femaleAvatar');
const femaleAvatarPreview = document.querySelector('#femalePreview');

maleAvatarUpload.addEventListener("change", evt => {
  const file = evt.target.files[0];
  if (file) {
      const reader = new FileReader();
      reader.addEventListener("load", e => {
        maleAvatarPreview.src = e.target.result;
        maleAvatarPreview.style.display = 'block';
      });

      reader.readAsDataURL(file);
  }
});

femaleAvatarUpload.addEventListener("change", evt => {
  const file = evt.target.files[0];
  if (file) {
      const reader = new FileReader();
      reader.addEventListener("load", e => {
        femaleAvatarPreview.src = e.target.result;
        femaleAvatarPreview.style.display = 'block';
      });

      reader.readAsDataURL(file);
  }
});
