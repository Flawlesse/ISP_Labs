import React from 'react';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { axiosInstance } from '../../database/axios.js'
import { Redirect } from 'react-router-dom'

class LoginForm extends React.Component {
    constructor(props) {
        super(props)
        this.state = {
            username: '',
            password: '',
            hasErrors: false,
            errors: null,
        }
        this.login = props.appLogin
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
                    errors: null,
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
        let formData = new FormData();
        formData.append('username', this.state.username)
        formData.append('password', this.state.password)

        axiosInstance.post('accounts/login/', formData)
            .then((response) => {
                // console.log(response)
                window.localStorage.setItem('access_token', response.data.token)
                window.dispatchEvent(new StorageEvent('storage', {
                    storageArea: window.localStorage,
                    key: "access_token",
                    newValue: response.data.token,
                }))
                this.login()
                this.setState(({
                    redirect: true,
                }))
            })
            .catch((errors) => {
                // console.log(errors.response.data);
                let errorstring = ""
                for (let key in errors.response.data) {
                    errorstring += errors.response.data[key] + '\n'
                }
                this.setState(({
                    hasErrors: true,
                    errors: errorstring,
                }))
                this.clearErrors()
            })
    }

    render() {
        if (this.state.redirect) {
            return <Redirect to={`/accounts/${this.state.username}`}></Redirect>
        }
        return (
            <div className="flex-container-col inverse-cetner" style={{ paddingTop: '20vh' }}>
                <div className="auth-form-wrapper">
                    <div className="auth-logo">
                        Вход
                    </div>
                    {
                        this.state.errors &&
                        <div className="errorlist">
                            {this.state.errors}
                        </div>
                    }
                    <form method="POST" onSubmit={this.handleSubmit}>
                        <div className="fieldWrapper">
                            <label htmlFor="username">
                                <FontAwesomeIcon icon={['fas', 'user']} />
                            </label>
                            <input type="text" required maxLength="150" name="username" id="username" placeholder="Имя пользователя..." onChange={this.handleChange}></input>
                        </div>
                        <div className="fieldWrapper">
                            <label htmlFor="password">
                                <FontAwesomeIcon icon={['fas', 'key']} />
                            </label>
                            <input type="password" required maxLength="128" name="password" id="password" placeholder="Пароль..." onChange={this.handleChange}></input>
                        </div>
                        <div className="submit-btn">
                            <button type="submit">Войти</button>
                        </div>
                    </form>
                </div>
            </div>
        )
    }
}

export default LoginForm;