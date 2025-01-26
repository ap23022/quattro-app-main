$(document).ready(function () {
  $(".add-btn").click(function () {
    const productId = $(this).data("productid");
    const userId = $(this).data("userid");

    // AJAX POST Request
    $.ajax({
      url: `/addtocart/${userId}/${productId}`,
      type: "POST",
      success: function (response) {
          alert("Added to cart successfully;!")
      },
      error: function () {
          alert("Failed to add to cart.");
      },
    });
  });

  $("#increase_stock").click(function () {
    const increase_by = $("#stock_added").val();
    const productId = $(this).data("productid");

    console.log(productId);

    $.ajax({
      url: `/admin/products/increase_stock/${productId}/${increase_by}`,
      type: "POST",
      success: function (response) {
          alert("Stock increased successfully!");
      },
      error: function () {
          alert("Failed to increase stock.");
      },
    });
  });

  $("#reduce_stock").click(function () {
    const decrease_by = $("#stock_reduced").val();
    const productId = $(this).data("productid");

    console.log(productId);

    $.ajax({
      url: `/admin/products/reduce_stock/${productId}/${decrease_by}`,
      type: "POST",
      success: function (response) {
          alert("Stock reduced successfully!");
      },
      error: function (response) {
        const jsonResponse = JSON.parse(response.responseText);
        errorMessage = jsonResponse.message;

        alert(errorMessage);
      },
    });
  });
});
