const maleAvatarUpload = document.querySelector('#maleAvatar');
const maleAvatarPreview = document.querySelector('#malePreview');

const femaleAvatarUpload = document.querySelector('#femaleAvatar');
const femaleAvatarPreview = document.querySelector('#femalePreview');

const audioUpload = document.querySelector('#audioUpload');
const audioPreview = document.querySelector('#audioPreview');

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

audioUpload.addEventListener("change", evt => {
  const file = evt.target.files[0];
  if (file) {
      const reader = new FileReader();
      reader.addEventListener("load", e => {
        audioPreview.src = e.target.result;
        audioPreview.style.display = 'block';
      });

      reader.readAsDataURL(file);
  }
});
