function showLoading() {
  document.getElementById("loadingOverlay").style.display = "flex";
}

function hideLoading() {
  document.getElementById("loadingOverlay").style.display = "none";
}


function generateExcel() {
  //calling a function to get a form data

   showLoading()
  const formData = getFormData();

  console.log(formData);

  fetch("http://localhost:8080/generate-excel", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(formData),
  })
    .then((response) => response.blob())
    .then((blob) => {
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.style.display = "none";
      a.href = url;
      a.download = "auction_data.xlsx";

      document.body.appendChild(a);

      a.click();
      window.URL.revokeObjectURL(url);
      hideLoading()
    })
    .catch((error) => console.error("Error generating Excel file:", error));
}

function getFormData() {
  // Get form data
  const auctionId = document.getElementById("auctionId").value;
  const category = document.getElementById("category").value;
  const bankName = document.getElementById("bankName").value;
  const state = document.getElementById("state").value;
  const city = document.getElementById("city").value;
  const area = document.getElementById("area").value;
  const maxPrice = document.getElementById("maxPrice").value;
  const minPrice = document.getElementById("minPrice").value;
  const auctionStartDate = document.getElementById("auctionStartDate").value;
  const auctionEndDate = document.getElementById("auctionEndDate").value;
  const tenderLastDate = document.getElementById("tenderLastDate").value;
  // Return as an object
  return {
    auctionId,
    category,
    bankName,
    state,
    city,
    area,
    maxPrice,
    minPrice,
    auctionStartDate,
    auctionEndDate,
    tenderLastDate,
  };
}
