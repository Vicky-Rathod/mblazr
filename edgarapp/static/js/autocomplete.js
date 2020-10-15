// Autocomplete
$(document).ready(function () {

    function autocomplete(inp, arr) {
        /*the autocomplete function takes two arguments,
        the text field element and an array of possible autocompleted values:*/
        var currentFocus, currentTicker;
        /*execute a function when someone writes in the text field:*/
        inp.addEventListener("input", function (e) {
            $('.autocomplete').removeClass('h-300')
            var a, b, i, val = this.value;
            /*close any already open lists of autocompleted values*/
            closeAllLists();
            if (!val) { return false; }
            currentFocus = -1;
            /*create a DIV element that will contain the items (values):*/
            a = document.createElement("DIV");
            a.setAttribute("id", this.id + "autocomplete-list");
            a.setAttribute("class", "autocomplete-items col-md-12 hidden");
            /*append the DIV element as a child of the autocomplete container:*/
            this.parentNode.appendChild(a);
            arr = filterTickers(val)
            counter = 0;
            /*for each item in the array...*/
            for (i = 0; i < arr.length; i++) {
                // if (counter == 4) break
                // counter++;
                /*check if the item starts with the same letters as the text field value:*/
                /*create a DIV element for each matching element:*/
                b = document.createElement("DIV");
                /*make the matching letters bold:*/
                b.innerHTML = "<a class='link' href='/filing/?q=" + arr[i].ticker + "&fid=all'><span>" + arr[i].ticker + "</span> - " + arr[i].name + "</a>";
                /*insert a input field that will hold the current array item's value:*/
                b.innerHTML += "<input type='hidden' value='" + arr[i].name + "'>";
                currentTicker = arr[i].ticker
                /*execute a function when someone clicks on the item value (DIV element):*/
                b.addEventListener("click", function (e) {
                    /*insert the value for the autocomplete text field:*/
                    inp.value = this.getElementsByTagName("input")[0].value;
                    this.getElementsByClassName('link')[0].click()
                    /*close the list of autocompleted values,
                    (or any other open lists of autocompleted values:*/
                    closeAllLists();
                });
                a.appendChild(b);
            }
            if (arr.length) {
                a.classList.remove('hidden');
                $('.autocomplete').addClass('h-300')
            }
        });

        /*execute a function presses a key on the keyboard:*/
        inp.addEventListener("keydown", function (e) {
            var x = document.getElementById(this.id + "autocomplete-list");
            if (x) x = x.getElementsByTagName("div");
            if (e.keyCode == 40) {
                /*If the arrow DOWN key is pressed,
                increase the currentFocus variable:*/
                currentFocus++;
                /*and and make the current item more visible:*/
                addActive(x);
            } else if (e.keyCode == 38) { //up
                /*If the arrow UP key is pressed,
                decrease the currentFocus variable:*/
                currentFocus--;
                /*and and make the current item more visible:*/
                addActive(x);
            } else if (e.keyCode == 13) {
                /*If the ENTER key is pressed, prevent the form from being submitted,*/
                e.preventDefault();
                if (currentFocus > -1) {
                    /*and simulate a click on the "active" item:*/
                    if (x) x[currentFocus].click();
                }
            }
        });
        function addActive(x) {
            /*a function to classify an item as "active":*/
            if (!x) return false;
            /*start by removing the "active" class on all items:*/
            removeActive(x);
            if (currentFocus >= x.length) currentFocus = 0;
            if (currentFocus < 0) currentFocus = (x.length - 1);
            /*add class "autocomplete-active":*/
            x[currentFocus].classList.add("autocomplete-active");
        }
        function removeActive(x) {
            /*a function to remove the "active" class from all autocomplete items:*/
            for (var i = 0; i < x.length; i++) {
                x[i].classList.remove("autocomplete-active");
            }
        }
        function closeAllLists(elmnt) {
            /*close all autocomplete lists in the document,
            except the one passed as an argument:*/
            var x = document.getElementsByClassName("autocomplete-items");
            for (var i = 0; i < x.length; i++) {
                if (elmnt != x[i] && elmnt != inp) {
                    x[i].parentNode.removeChild(x[i]);
                }
            }
        }
        /*execute a function when someone clicks in the document:*/
        document.addEventListener("click", function (e) {
            closeAllLists(e.target);
        });
    }

    var tickers;

    fetch("/static/bootstrap/js/tickers.json").then(response => response.json())
        .then(d => {
            tickers = d.sort(function (a, b) {
                var x = a.ticker.toLowerCase();
                var y = b.ticker.toLowerCase();
                if (x < y) { return -1; }
                if (x > y) { return 1; }
                return 0;
            })
            autocomplete(document.getElementById("myInput"), tickers);
        });


    function filterTickers(value) {
        value = value.toLowerCase()
        let suggestions = tickers.filter(s => {
            // if (value.length && (s.name.toLowerCase().indexOf(value) != -1 || s.ticker.toLowerCase().indexOf(value) != -1)) return true;
            if (s.ticker.toLowerCase().substr(0, value.length) == value) return true;
            return false
        })
        if (suggestions.length < 10) {
            // suggestions.concat()
            let others = tickers.filter(s => {
                // if (value.length && (s.name.toLowerCase().indexOf(value) != -1 || s.ticker.toLowerCase().indexOf(value) != -1)) return true;
                // if (s.ticker.toLowerCase().substr(0, value.length) == value) return true;
                if (s.name.toLowerCase().substr(0, value.length) == value) return true;
                return false
            })
            suggestions = suggestions.concat(others)
            // console.log(others)

        }
        // suggestions = suggestions

        function onlyUnique(value, index, self) {
            return self.indexOf(value) === index;
        }

        return suggestions.filter(onlyUnique)
    }
})
