import React from 'react';
import { Redirect } from 'react-router-dom'
import loadgif from '../../assets/loading.gif'
import { axiosInstance } from '../../database/axios'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';

class OrderForm extends React.Component {
    constructor(props) {
        super(props)
        console.log(props);
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
            redirect: false,
        }
        this.isloggedIn = props.isLoggedIn
        this.timerID = null
    }
    componentDidMount() {
        if (this.state.loading) {
            if (this.state.action === "update") {
                axiosInstance.get(`/orders/${this.state.id}/`)
                    .then((response) => response.data)
                    .then((data) => {
                        this.setState({
                            title: data.title,
                            description: data.description,
                            price: data.price,
                            loading: false,
                        })
                    })
                    .catch((errors) => {
                        console.log(errors.response.data);
                    })
            }
            this.setState({ loading: false })
        }
    }
    componentDidUpdate() {
        if (!this.state.hasErrors) {
            clearTimeout(this.timerID)
            this.timerID = null
        }
    }

    clearErrors = () => {
        if (this.timerID === null) {
            this.timerID = setTimeout(() => {
                this.setState(({
                    fieldErrors: {
                        title: null,
                        price: null,
                    },
                    hasErrors: false,
                }))
            }, 5000);
        }
    }


    handleChange = (e) => {
        this.setState(({
            [e.target.name]: e.target.value
        }))
    }
    handleSubmit = (e) => {
        e.preventDefault();
        let { profile_pic_preview, fieldErrors, ...postData } = this.state;

        if (this.state.action === "create") {
            axiosInstance.post('orders/', postData)
                .then((response) => response.data)
                .then((data) => {
                    console.log(data);
                    this.setState(({
                        redirect: true,
                    }))
                })
                .catch((errors) => {
                    let newFieldErrors = {}
                    console.log(errors.response.data);
                    for (let key in errors.response.data) {
                        if (key in this.state.fieldErrors) {
                            newFieldErrors[key] = errors.response.data[key]
                        }
                    }
                    this.setState(({
                        hasErrors: true,
                        fieldErrors: newFieldErrors,
                    }))
                    this.clearErrors()
                })
        }
        else {
            axiosInstance.put(`orders/${this.state.id}/`, postData)
                .then((response) => response.data)
                .then((data) => {
                    console.log(data);
                    this.setState(({
                        redirect: true,
                    }))
                })
                .catch((errors) => {
                    let newFieldErrors = {}
                    console.log(errors.response.data);
                    for (let key in errors.response.data) {
                        if (key in this.state.fieldErrors) {
                            newFieldErrors[key] = errors.response.data[key]
                        }
                    }
                    this.setState(({
                        hasErrors: true,
                        fieldErrors: newFieldErrors,
                    }))
                    this.clearErrors()
                })
        }
    }

    render() {
        if (!this.isloggedIn) {
            // message about you're not logged in
            return <Redirect to='/orders/'></Redirect>
        }

        if (this.state.loading) {
            return <div className="flex-container align-center" style={{ marginTop: '10vh' }}><img src={loadgif}></img></div>
        }
        if (this.state.redirect) {
            return <Redirect to='/orders/'></Redirect>
        }

        return (
            <div className="flex-container-col inverse-cetner" style={{ paddingTop: '10vh' }}>
                <div className="order-form-wrapper">
                    <div className="order-logo">
                        Заказ
                    </div>
                    <form onSubmit={this.handleSubmit}>
                        {this.state.fieldErrors.title &&
                            <div className="errorlist">
                                {this.state.fieldErrors.title}
                            </div>
                        }
                        <div className="fieldWrapper">
                            <label htmlFor="title">
                                <FontAwesomeIcon icon={['fas', 'heading']} />
                            </label>
                            <input
                                type="text"
                                required
                                maxLength="100"
                                name="title"
                                id="title"
                                placeholder="Заголовок..."
                                value={this.state.title}
                                onChange={this.handleChange}
                            >
                            </input>
                        </div>
                        <div className="fieldWrapper">
                            <textarea
                                rows="20"
                                cols="35"
                                name="description"
                                id="description"
                                placeholder="  Описание заказа"
                                value={this.state.description}
                                onChange={this.handleChange}
                            >
                            </textarea>
                        </div>
                        {this.state.fieldErrors.price &&
                            <div className="errorlist">
                                {this.state.fieldErrors.price}
                            </div>
                        }
                        <div className="fieldWrapper">
                            <label htmlFor="title">
                                <FontAwesomeIcon icon={['fas', 'dollar-sign']} />
                            </label>
                            <input
                                type="number"
                                required
                                name="price"
                                id="price"
                                step="0.01"
                                placeholder="Цена заказа..."
                                value={this.state.price}
                                onChange={this.handleChange}
                            >
                            </input>
                        </div>

                        <div className="submit-btn">
                            <button type="submit">{this.state.action === "create" ? 'Создать' : 'Обновить'}</button>
                        </div>
                    </form>
                </div>
            </div>
        );
    }
}

export default OrderForm;