import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import React from 'react'
import { Link } from 'react-router-dom'
import { axiosInstance } from '../../database/axios'
import defpic from '../../assets/no_pic.jpeg'
import { Redirect } from 'react-router-dom'
import loadgif from '../../assets/loading.gif'


class OrderItem extends React.Component {
    constructor(props) {
        super(props)
        this.state = {
            id: props.match ? props.match.params.id : (props.id ? props.id : null),
            triggerListUpdate: props.triggerListUpdate ? props.triggerListUpdate : null,
            isItem: props.isItem,

            author: {},
            executor: {},
            title: '',
            price: '',
            date_posted: '', // string repr date
            description: '',
            executor_wallet: 'Не выбран.',
            orderer_wallet: 'Не выбран.',
            order_state: 'Неизвестно',

            can_edit: false,
            can_accept: false,
            can_reject: false,

            can_pick_ord_wallet: false,
            can_pick_exec_wallet: false,

            can_pay_and_delete: false,

            redirect: false,
            action_happened: props.shouldUpdate ? props.shouldUpdate : false,
            loading: true,
        }
    }
    componentDidMount() {
        this.refetch()
    }
    componentDidUpdate() {
        console.log(`Called on ${this.state.id}`);
        if (this.state.redirect) {
            return;
        }
        if (this.state.action_happened) {
            this.refetch()
            if (this.state.triggerListUpdate) {
                this.state.triggerListUpdate()
            }
            this.setState({ action_happened: false })
        }
    }

    refetch = () => {
        axiosInstance.get(`/orders/${this.state.id}/`)
            .then((response) => {
                let data = response.data
                console.log(data);
                // here, data.author and data.executor are still strings
                axiosInstance.get(`/accounts/${data.author}/`)
                    .then((response) => {
                        const actualAuthor = response.data
                        data.author = actualAuthor

                        if (data.executor) {
                            axiosInstance.get(`/accounts/${data.executor}/`)
                                .then((response) => {
                                    const actualExecutor = response.data
                                    data.executor = actualExecutor
                                    this.setState({ ...data, loading: false, })
                                })
                                .catch((errors) => {
                                    console.log(errors.response)
                                })
                        }
                        else {
                            data.executor = {}
                            this.setState({ ...data, loading: false })
                        }

                    })
                    .catch((errors) => {
                        console.log(errors.response)
                    })
            })
            .catch((errors) => {
                console.log(errors.response)
                this.setState(({ redirect: true }))
            })
    }

    handleOrderAccept = (e) => {
        if (window.confirm("Вы действительно хотите принять данный заказ?")) {
            axiosInstance.patch(`/orders/${this.state.id}/perform_action/`, { accept_order: true })
                .then((response) => {
                    console.log(response.data.success)
                    this.setState(({ action_happened: true }))
                })
                .catch((errors) => {
                    console.log(errors.response)
                })
        }
    }
    handleOrderReject = (e) => {
        if (window.confirm("Вы действительно хотите отказаться от данного заказа?")) {
            axiosInstance.patch(`/orders/${this.state.id}/perform_action/`, { reject_order: true })
                .then((response) => {
                    console.log(response.data.success)
                    this.setState(({ action_happened: true }))
                })
                .catch((errors) => {
                    console.log(errors.response);
                })
        }
    }
    handleOrderDelete = (e) => {
        if (window.confirm("Вы действительно хотите удалить данный заказ?")) {
            axiosInstance.delete(`/orders/${this.state.id}/`)
                .then((response) => {
                    console.log(response.data.success);
                    this.setState(({
                        redirect: true,
                    }))
                })
        }
    }
    handlePayAndDelete = (e) => {
        axiosInstance.patch(`/orders/${this.state.id}/perform_action/`, { "pay_and_delete": true })
            .then((response) => {
                console.log(response.data.success);
                this.setState(({
                    redirect: true,
                }))
            })
            .catch((errors) => {
                console.log(errors.response.data.detail);
            })
    }
    handleWalletChange = (e) => {
        let data = {}
        if (e.target.name === "executor-wallet-select") {
            data.pick_exec_wallet = e.target.value
        }
        else {
            data.pick_ord_wallet = e.target.value
        }

        console.log(e.target.value);
        axiosInstance.patch(`/orders/${this.state.id}/perform_action/`, data)
            .then((response) => {
                console.log(response.data.success);
                this.setState(({ action_happened: true }))
            })
            .catch((errors) => {
                console.log(errors.response.data.detail);
            })
    }

    render() {
        if (this.state.loading) {
            return <div className="flex-container align-center"><img src={loadgif}></img></div>
        }

        if (this.state.redirect) {
            console.log("redirecting...");
            return <Redirect to='/'></Redirect>
        }

        function isEmptyObj(obj) {
            return Object.keys(obj).length === 0;
        }

        const has_executor = !isEmptyObj(this.state.executor)


        return (
            <div className="flex-container order-section">
                <div className="grid-container-outer order" style={{ border: "2px solid black" }}>
                    <div className="grid-item flex-container-col align-up" style={{ paddingLeft: "10px" }}>
                        <Link to={`/accounts/${this.state.author.username}`}>
                            <img src={this.state.author.profile_pic ? this.state.author.profile_pic : defpic} alt="NO IMAGE PROVIDED" className="round-thumbnail-200 author-pic" />
                        </Link>
                    </div>
                    <div className="grid-item grid-container-inner-order-detail">
                        <div className="grid-item flex-container align-right inverse-center order-action-group">
                            <p className="date" style={{ marginRight: "7%" }}>
                                {(new Date(this.state.date_posted)).toLocaleString('ru-ru', { timeZone: 'UTC' })}
                            </p>
                            {
                                this.state.can_edit &&
                                <span>
                                    <Link to={`/orders/${this.state.id}/update`} className="order-edit-link"><FontAwesomeIcon icon={["fas", "edit"]} /></Link>
                                    <span className="order-delete-link" onClick={this.handleOrderDelete}><FontAwesomeIcon icon={["fas", "trash"]} /></span>
                                </span>
                            }

                            {
                                this.state.can_accept &&
                                <span onClick={this.handleOrderAccept} className="order-accept-link">
                                    <FontAwesomeIcon icon={["fas", "plus-circle"]} />
                                </span>
                            }

                            {
                                this.state.can_reject &&
                                <span onClick={this.handleOrderReject} className="order-reject-link">
                                    <FontAwesomeIcon icon={["fas", "times-circle"]} />
                                </span>
                            }
                        </div>
                        <div className="grid-item flex-container-col align-left order-content">
                            <div className="order-content">
                                <div className="title">
                                    <span>{this.state.title}</span>
                                </div>
                                <hr />
                                {
                                    this.state.isItem
                                        ?
                                        <p>
                                            {this.state.description.length > 100 ? this.state.description.slice(0, 100) + "..." : this.state.description}
                                        </p>
                                        :
                                        <p>{this.state.description}</p>
                                }
                                <p>
                                    Исполнитель:
                                    {
                                        has_executor
                                            ?
                                            <Link to={`/accounts/${this.state.executor.username}`}>{this.state.executor.username}</Link>
                                            :
                                            <span>{'  '}Нету.</span>
                                    }
                                </p>
                                <p className="flex-container space-even">
                                    <span>
                                        Кошелёк исполнителя:
                                        {
                                            this.state.can_pick_exec_wallet
                                                ?
                                                <select
                                                    name="executor-wallet-select"
                                                    value={this.state.executor_wallet ? this.state.executor_wallet.split(' ')[0] : 'null'}
                                                    onChange={this.handleWalletChange}
                                                >
                                                    <option key='null' value='null'>Не выбран.</option>
                                                    {this.state.executor.wallets.map((wallet_str) => (
                                                        <option key={wallet_str} value={wallet_str.split(' ')[0]}>
                                                            {wallet_str}
                                                        </option>
                                                    ))
                                                    }
                                                </select>
                                                :
                                                <span>
                                                    <FontAwesomeIcon icon={["fas", "wallet"]} />
                                                    {this.state.executor_wallet}
                                                </span>
                                        }
                                    </span>
                                    <span>
                                        Кошелёк заказчика:
                                        {
                                            this.state.can_pick_ord_wallet
                                                ?
                                                <select
                                                    name="orderer-wallet-select"
                                                    value={this.state.orderer_wallet ? this.state.orderer_wallet.split(' ')[0] : 'null'}
                                                    onChange={this.handleWalletChange}
                                                >
                                                    <option key='null' value='null'>Не выбран.</option>
                                                    {this.state.author.wallets.map((wallet_str) => (
                                                        <option key={wallet_str} value={wallet_str.split(' ')[0]} >
                                                            {wallet_str}
                                                        </option>
                                                    ))
                                                    }
                                                </select>
                                                :
                                                <span>
                                                    <FontAwesomeIcon icon={["fas", "wallet"]} />
                                                    {this.state.orderer_wallet}
                                                </span>
                                        }
                                    </span>
                                </p>
                                <div className="flex-container inverse-center space-around">
                                    <div className={`${this.state.order_state} order-state`}>
                                        {this.state.order_state}
                                    </div>
                                    <p className="price">${this.state.price}</p>
                                </div>
                            </div>
                        </div>

                        <div className="grid-item flex-container align-center order-btn-group">
                            {
                                this.state.can_pay_and_delete
                                    ?
                                    <button type="button" className="pay-order-btn" onClick={this.handlePayAndDelete}>Оплатить заказ</button>
                                    :
                                    null
                            }
                            {
                                this.state.isItem
                                    ?
                                    <Link to={`/orders/${this.state.id}`}>
                                        <button type="button" className="detail-order-btn">Подробнее</button>
                                    </Link>
                                    :
                                    <Link to="/orders">
                                        <button type="button" className="all-orders-btn">Все заказы</button>
                                    </Link>
                            }
                        </div>
                    </div>
                </div>
            </div>
        );
    }
}

export default OrderItem;