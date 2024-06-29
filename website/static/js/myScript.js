$('.plus-cart').click(function(){
    var id = $(this).attr('pid').toString();
    var quantity = this.parentNode.children[2];
    
    $.ajax({
        type: 'GET',
        url: '/pluscart',
        data: {
            cart_id: id
        },
        success: function(data){
            quantity.innerText = data.quantity;
            document.getElementById(`quantity${id}`).innerText = data.quantity;
            document.getElementById('amount_tt').innerText = data.amount;
            document.getElementById('totalamount').innerText = data.total;

            
        }
    });
});


$('.minus-cart').click(function(){
    console.log('Button clicked');

    var id = $(this).attr('pid').toString();
    var quantityElement = this.parentNode.children[2];
    var currentQuantity = parseInt(quantityElement.innerText);

    // Check if the current quantity is already 1
    if (currentQuantity > 1) {
        // Only proceed if the current quantity is greater than 1
        $.ajax({
            type: 'GET',
            url: '/minuscart',
            data: {
                cart_id: id
            },
            success: function(data){
                console.log(data);
                quantityElement.innerText = data.quantity;
                document.getElementById(`quantity${id}`).innerText = data.quantity;
                document.getElementById('amount_tt').innerText = data.amount;
                document.getElementById('totalamount').innerText = data.total;
            }
        });
    } else {
        // Show the notification box
        $('#notification-box').fadeIn(300).delay(2000).fadeOut(300);
    }
});




$('.remove-cart').click(function(){
    
    var id = $(this).attr('pid').toString()

    var to_remove = this.parentNode.parentNode.parentNode.parentNode

    $.ajax({
        type: 'GET',
        url: '/removecart',
        data: {
            cart_id: id
        },

        success: function(data){
            document.getElementById('amount_tt').innerText = data.amount
            document.getElementById('totalamount').innerText = data.total
            to_remove.remove()
        }
    })


})
