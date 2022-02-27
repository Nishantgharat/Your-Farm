window.addEventListener("DOMContentLoaded", (event) => {
  var updateBtns = document.querySelectorAll(".update-cart");
  console.log(updateBtns);
  var commentForm = document.querySelector(".commentForm");
  commentForm &&
    commentForm.addEventListener("submit", (e) => {
      // Store reference to form to make later code easier to read
      const form = commentForm;

      // Post data using the Fetch API
      fetch(form.action, {
        method: form.method,
        body: new FormData(form),
      }).then(() => {
        location.reload();
      });
      // Prevent the default form submit
      e.preventDefault();
    });

  updateBtns.forEach((btn) => {
    btn.addEventListener("click", (e) => {
      var productId = btn.dataset.product;
      var action = btn.dataset.action;
      console.log("productId:", productId, "action:", action);
      updateUserOrder(productId, action);
      e.preventDefault();
      e.stopImmediatePropagation();
    });
  });

  // stripe payment
  
  var checkoutButton = $("#placeorder");

  checkoutButton &&
    checkoutButton.on("click", function (event) {
      console.log('print')
      event.target.innerHTML = event.target.innerText + 
      `<div class="spinner-border spinner-border-sm ml-3" role="status">
      <span class="sr-only">Loading...</span>
      </div>`;
      event.target.disabled = true;
      checkout();
    });

  var updateWishlistBtns = document.querySelectorAll(".update-wishlist");
  updateWishlistBtns.forEach((btn) => {
    btn.addEventListener("click", (e) => {
      var productId = btn.dataset.product;
      var action = btn.dataset.action;
      console.log("productId:", productId, "action:", action);
      updateWishlist(productId, action);
      e.preventDefault();
      e.stopImmediatePropagation();
    });
  });

  var modalEnablers = document.querySelectorAll("#modalEnabler");
  modalEnablers.forEach((btn) => {
    btn.addEventListener("click", (e) => {
      var productId = btn.dataset.product;
      showModal(productId);
      e.preventDefault();
      // e.stopImmediatePropagation()
    });
  });
});

function checkout() {

  var stripe = Stripe(
    "pk_test_51IlaP8SGn4fFAGW5H8vfHfcGuTbMeXcGALhRExQmasivUIKpOJ8LKIdJgDxRWJDRDJtcM7BiE7qtS7mEG8IAJLha00BrU1ibp9"
  );
  
  const csrftoken = getCookie("csrftoken");
  fetch("/create-checkout-session", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-CSRFToken": csrftoken,
    },
  })
    .then(function (response) {
      return response.json();
    })
    .then(function (session) {
      return stripe.redirectToCheckout({ sessionId: session.id });
    })
    .then(function (result) {
      // If redirectToCheckout fails due to a browser or network
      // error, you should display the localized error message to your
      // customer using error.message.
      if (result.error) {
        alert(result.error.message);
      }
    })
    .catch(function (error) {
      console.error("Error:", error);
    });
}

function updateUserOrder(productId, action) {
  console.log("User is logged in, sending data..");
  var url = "/update_item";
  const csrftoken = getCookie("csrftoken");
  fetch(url, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-CSRFToken": csrftoken,
    },
    body: JSON.stringify({ productId: productId, action: action }),
  })
    .then((response) => {
      return response.json();
    })
    .then((data) => {
      location.reload();
    });
}

function updateWishlist(productId, action) {
  var url = "/update_wishlist";
  const csrftoken = getCookie("csrftoken");
  fetch(url, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-CSRFToken": csrftoken,
    },
    body: JSON.stringify({ productId: productId, action: action }),
  })
    .then((response) => {
      return response.json();
    })
    .then((data) => {
      location.reload();
    });
}
function showModal(productId) {
  var url = "/modal";
  const csrftoken = getCookie("csrftoken");
  fetch(url, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-CSRFToken": csrftoken,
    },
    body: JSON.stringify({ productId: productId }),
  })
    .then((response) => {
      return response.json();
    })
    .then((data) => {
      console.log(data);
      let modal = document.querySelector(".modal-content");
      modal.innerHTML = `
        <div class="modal-body p-0">
        <div class="row align-items-stretch">
          <div class="col-lg-6 p-lg-0">
          <a class="product-view d-block h-100 bg-cover bg-center" title="${
            data.name
          }" style="background: url(${data.image})" href="${
        data.image
      }" data-lightbox="productview" title="${data.name}"></a>
         </div>
          <div class="col-lg-6">
            <button class="close p-4" type="button" data-dismiss="modal" aria-label="Close"><span aria-hidden="true">×</span></button>
            <div class="p-5 my-md-4">
              <h2 class="h4">${data.name}</h2>
              <p class="text-muted">$${data.sell_price}</p>
              <p class="text-small mb-4">${
                data.description.length > 250
                  ? `${data.description.substring(0, 250)}...`
                  : data.description
              }</p>
              <div class="row align-items-stretch mb-4">
                <div class="col-sm-7 pr-sm-0">
                  <div class="border d-flex align-items-center justify-content-between py-1 px-3"><span class="small text-uppercase text-gray mr-4 no-select">Quantity</span>
                    <div class="quantity">
                      <button class="dec-btn p-0"><i class="fas fa-caret-left"></i></button>
                      <input class="form-control border-0 shadow-0 p-0" type="text" value="1">
                      <button class="inc-btn p-0"><i class="fas fa-caret-right"></i></button>
                    </div>
                  </div>
                </div>
                <div class="col-sm-5 pl-sm-0"><a class="btn btn-dark btn-sm btn-block h-100 d-flex align-items-center justify-content-center px-0" href="cart.html">Add to cart</a></div>
              </div><a class="btn btn-link text-dark p-0" href="#"><i class="far fa-heart mr-2"></i>Add to wish list</a>
            </div>
          </div>
        </div>
      </div>
      `;
      // location.reload()
    });
}

function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== "") {
    const cookies = document.cookie.split(";");
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      // Does this cookie string begin with the name we want?
      if (cookie.substring(0, name.length + 1) === name + "=") {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}

function onSelectChange() {
  var selectedValue = document.getElementById("img_choice").value;
  if (selectedValue == "1") {
    document.getElementById("url").disabled = false;
    document.getElementById("browse").disabled = true;
  } else {
    document.getElementById("url").disabled = true;
    document.getElementById("browse").disabled = false;
  }
}
