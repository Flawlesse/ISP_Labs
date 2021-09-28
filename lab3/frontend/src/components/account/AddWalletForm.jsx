import React from 'react'
import { Redirect } from 'react-router-dom'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { axiosInstance } from '../../database/axios'

class AddWalletForm extends React.Component {
    constructor(props) {
        super(props)
        this.state = {
            name: '',
            password: '',

            isLoggedIn: props.isLoggedIn,
            redirect: false,
            fieldErrors: {
                name: null,
                password: null,
            },
            hasErrors: false,
        }
        this.timerID = null
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
                        name: null,
                        password: null,
                    },
                    hasErrors: false,
                }))
            }, 5000);
        }
    }


    handleChange = (e) => {
        this.setState({
            [e.target.name]: e.target.value,
        })
    }

    handleSubmit = (e) => {
        e.preventDefault()
        const { name, password } = this.state
        const data = { name, password }

        axiosInstance.post('wallets/add/', data)
            .then((response) => {
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

    render() {
        if (this.state.redirect) {
            return <Redirect to="/profile" />
        }
        return (
            <div className="flex-container-col inverse-cetner" style={{ paddingTop: '20vh' }}>
                <div className="wallet-form-wrapper">
                    <div className="wallet-logo">
                        Добавление<br />кошелька
                    </div>
                    <form onSubmit={this.handleSubmit}>
                        {
                            this.state.fieldErrors.name &&
                            <div className="errorlist">
                                {this.state.fieldErrors.name}
                            </div>
                        }
                        <div className="fieldWrapper">
                            <label htmlFor="name">
                                <FontAwesomeIcon icon={['fas', 'user']} />
                            </label>
                            <input type="text" required maxLength="40" name="name" id="name" placeholder="Имя кошелька..." onChange={this.handleChange}></input>
                        </div>
                        {
                            this.state.fieldErrors.password &&
                            <div className="errorlist">
                                {this.state.fieldErrors.password}
                            </div>
                        }
                        <div className="fieldWrapper">
                            <label htmlFor="password">
                                <FontAwesomeIcon icon={['fas', 'key']} />
                            </label>
                            <input type="password" required maxLength="128" name="password" id="password" placeholder="Пароль..." onChange={this.handleChange}></input>
                        </div>
                        <div className="submit-btn">
                            <button type="submit">Добавить</button>
                        </div>
                    </form>
                </div>
            </div>
        )
    }
}

export default AddWalletForm;