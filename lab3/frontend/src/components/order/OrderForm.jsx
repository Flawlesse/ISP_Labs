import React from 'react';
import loadgif from '../../assets/loading.gif'

class OrderForm extends React.Component {
    constructor(props) {
        super(props)
        this.state = {
            action: props.action,
            id: props.action === "update" ? props.match.params.id : null,
            title: '',
            description: '',
            price: '0.01',
            hasErrors: false,
            fieldErrors: {
                title: null,
                price: null,
            },
            not_found: false,
            loading: true,
        }
    }
    componentDidMount() {

    }
    componentDidUpdate() {

    }



    render() {
        if (this.state.loading) {
            return <div className="flex-container align-center"><img src={loadgif}></img></div>
        }

        return (
            <div className="order-form-wrapper flex-container align-center">

            </div>
        );
    }
}

export default OrderForm;