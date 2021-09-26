import React, { Component } from 'react'
import { axiosInstance } from '../../database/axios'
import OrderItem from './OrderItem'
import { Link, Redirect } from 'react-router-dom'

class OrderList extends React.Component {
    constructor(props) {
        super(props)
        this.state = {
            searchParams: props.location.search,
            count: 0,
            next: null, // next page for pagination
            previous: null, // prev page for pagination
            currentPage: (new URLSearchParams(props.location.search)).get('page') ? (new URLSearchParams(props.location.search)).get('page') : 1,
            results: [],
            needListUpdate: false,
        }
    }
    componentDidMount() {
        this.refetch()
    }
    componentDidUpdate() {
        if (this.state.needListUpdate) {
            this.setState({ needListUpdate: false })
            window.location.reload()
        }
    }



    refetch = () => {
        axiosInstance.get(`/orders/${this.state.searchParams ? this.state.searchParams : ""}`)
            .then((response) => response.data)
            .then((data) => {
                this.setState({
                    ...data
                })
            })
            .catch((errors) => {
                console.log(errors.data);
            })
    }
    triggerUpdate = () => {
        console.log("-----IN TRIGGER UPDATE-----");
        this.setState({ needListUpdate: true })
    }

    render() {
        if (this.state.next) {
            console.log(new URLSearchParams(this.state.next.split('?')[1]).get('page'));
        }
        return (
            <div>
                <ul className="order-list">
                    {this.state.results.map((order) => (
                        <li key={order.id}>
                            <OrderItem
                                id={order.id}
                                triggerListUpdate={this.triggerUpdate}
                                shouldUpdate={this.state.needListUpdate}
                                isItem={true}
                            >
                            </OrderItem>
                        </li>
                    ))
                    }
                </ul>

                <div className="flex-container align-center" style={{ paddingBottom: "30px" }}>
                    <Link to="/orders/create">
                        <button type="button" className="create-order-btn">
                            Создать заказ
                        </button>
                    </Link>
                </div>

                <div className="paginator flex-container align-center">
                    {
                        this.state.previous &&
                        (
                            (new URLSearchParams(this.state.previous.split('?')[1])).get('page')
                                ?
                                <a href={`/orders/?page=${(new URLSearchParams(this.state.previous.split('?')[1])).get('page')}`} className="page-btn">
                                    &laquo;
                                </a>
                                :
                                <a href="/orders/" className="page-btn">
                                    &laquo;
                                </a>
                        )
                    }
                    {
                        this.state.count !== 0 &&
                        <span>Страница {this.state.currentPage} из {parseInt(this.state.count / 3 + 1, 10)}</span>
                    }
                    {
                        this.state.next &&
                        <a href={`/orders/?page=${(new URLSearchParams(this.state.next.split('?')[1])).get('page')}`} className="page-btn">
                            &raquo;
                        </a>
                    }
                </div>
            </div>
        );
    }
}

export default OrderList;