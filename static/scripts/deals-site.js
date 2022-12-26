/* Event handler for when a deal is favorited or unfavorited */
function favorite_change(deal_id) {
    var fav_checkbox = document.getElementById("favorite-" + deal_id);

    if (fav_checkbox.checked) {
        url = "/add_favorite/" + deal_id;

        var xhr = new XMLHttpRequest();
        xhr.open('POST', url, true); // async=true -> asynchronous
        xhr.onreadystatechange = function () {
            fieldData = JSON.parse(this.responseText);
            favorites = fieldData['favorites'];
            alert(favorites)
        }
    } else {
        url = "/del_favorite/" + deal_id;

        var xhr = new XMLHttpRequest();
        xhr.open('DELETE', url, true);
        xhr.onreadystatechange = function () {

        }
    }
}