(function () {
  console.log("ready!"); // sanity check
})();

const deleteElements = document.getElementsByClassName("delete");

for (var i = 0; i < deleteElements.length; i++) {
  deleteElements[i].addEventListener("click", function () {
    const postId = this.getAttribute("id");
    const node = document.getElementsByClassName("entry")[0];
    fetch(`/delete/${postId}`)
      .then(function (resp) {
        return resp.json();
      })
      .then(function (result) {
        if (result.status === 1) {
          node.parentNode.removeChild(node);
          console.log(result);
        }
        location.reload();
      })
      .catch(function (err) {
        console.log(err);
      });
  });
}