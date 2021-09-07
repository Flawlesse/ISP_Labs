let delete_order_link = document.querySelector('.order-delete-link');


delete_order_link.addEventListener('click', (e) => {
    if (confirm("Вы действительно хотите удалить данный заказ?") === false){
        e.preventDefault();
    }
})