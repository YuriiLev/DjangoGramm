function updateLikeButton(button, data) {
  button.classList.toggle("btn-danger", data.liked);
  button.classList.toggle("btn-outline-danger", !data.liked);

  const count = button.querySelector(".like-count");
  if (count) count.textContent = data.count;
}

function updateFollowButton(button, data) {
  button.classList.toggle("btn-secondary", data.following);
  button.classList.toggle("btn-primary", !data.following);

  const label = button.querySelector(".follow-label");
  if (label) label.textContent = data.following ? "Unfollow" : "Follow";

  const count = button.querySelector(".follow-count");
  if (count) count.textContent = data.count;
}

async function toggle(button, url, update) {
  button.classList.add("disabled");

  try {
    const response = await fetch(url, {
      headers: { "X-Requested-With": "XMLHttpRequest" },
    });

    if (!response.ok) throw new Error(response.status);

    update(button, await response.json());
  } catch (error) {
    console.error("Toggle failed:", error);
    window.location.href = url;
  } finally {
    button.classList.remove("disabled");
  }
}

document.addEventListener("click", (event) => {
  const likeButton = event.target.closest("[data-like-url]");
  if (likeButton) {
    event.preventDefault();
    toggle(likeButton, likeButton.dataset.likeUrl, updateLikeButton);
    return;
  }

  const followButton = event.target.closest("[data-follow-url]");
  if (followButton) {
    event.preventDefault();
    toggle(followButton, followButton.dataset.followUrl, updateFollowButton);
  }
});