import React from 'react';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import defpic from '../../assets/no_pic.jpeg'
import { axiosMultipartInstance } from '../../database/axios.js'
import { withRouter } from 'react-router-dom'
import { Redirect } from 'react-router-dom'

class RegisterForm extends React.Component {
    constructor(props) {
        super(props)
        this.state = {
            username: '',
            email: '',
            password: '',
            password2: '',
            first_name: '',
            last_name: '',
            phone_number: '',
            about: '',
            profile_pic_preview: defpic,
            profile_pic: null,
            hasErrors: false,
            fieldErrors: {
                username: null,
                email: null,
                password: null,
                password2: null,
                phone_number: null,
            },
            redirect: false,
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
                        username: null,
                        email: null,
                        password: null,
                        password2: null,
                        phone_number: null,
                    },
                    hasErrors: false,
                }))
            }, 5000);
        }
    }

    getImgData = () => {
        const picinput = document.getElementById('profile_pic')
        const file = picinput.files[0];
        if (file) {
            const fileReader = new FileReader()
            fileReader.readAsDataURL(file)
            const formComponent = this
            fileReader.addEventListener("load", function () {
                formComponent.setState((
                    {
                        profile_pic_preview: this.result,
                        profile_pic: file,
                    }
                ))
            })
        }
    }

    handleChange = (e) => {
        if (e.target.name === 'profile_pic') {
            this.getImgData();
        }
        else {
            this.setState(({
                [e.target.name]: e.target.value
            }))
        }
    }
    handleImageClick = (e) => {
        document.getElementById('profile_pic').click()
    }
    handleSubmit = (e) => {
        e.preventDefault();
        let { profile_pic_preview, fieldErrors, ...postData } = this.state;
        if (postData.profile_pic === null) {
            delete postData.profile_pic
        }
        let formData = new FormData();
        for (let key in postData) {
            formData.append(key, postData[key]);
        }

        axiosMultipartInstance.post('accounts/register/', formData)
            .then((response) => {
                window.localStorage.setItem('access_token', response.data.token)
                window.dispatchEvent(new StorageEvent('storage', {
                    storageArea: window.localStorage,
                    key: "access_token",
                    newValue: response.data.token,
                }))
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
            return <Redirect to='/profile'></Redirect>
        }
        return (
            <div className="flex-container-col inverse-cetner" style={{ paddingTop: '10vh' }}>
                <div className="auth-form-wrapper">
                    <div className="auth-logo">
                        Регистрация
                    </div>
                    <form onSubmit={this.handleSubmit}>
                        {(() => {
                            if (this.state.fieldErrors.username) {
                                return (
                                    <div className="errorlist">
                                        {this.state.fieldErrors.username}
                                    </div>
                                )
                            }
                        })()}
                        <div className="fieldWrapper">
                            <label htmlFor="username">
                                <FontAwesomeIcon icon={['fas', 'user']} />
                            </label>
                            <input type="text" required maxLength="150" name="username" id="username" placeholder="Имя пользователя..." onChange={this.handleChange}></input>
                        </div>
                        {(() => {
                            if (this.state.fieldErrors.email) {
                                return (
                                    <div className="errorlist">
                                        {this.state.fieldErrors.email}
                                    </div>
                                )
                            }
                        })()}
                        <div className="fieldWrapper">
                            <label htmlFor="email">
                                <FontAwesomeIcon icon={['fas', 'address-card']} />
                            </label>
                            <input type="email" required maxLength="254" name="email" id="email" placeholder="Эл. почта..." onChange={this.handleChange}></input>
                        </div>
                        {(() => {
                            if (this.state.fieldErrors.phone_number) {
                                return (
                                    <div className="errorlist">
                                        {this.state.fieldErrors.phone_number}
                                    </div>
                                )
                            }
                        })()}
                        <div className="fieldWrapper">
                            <label htmlFor="phone_number">
                                <FontAwesomeIcon icon={['fas', 'phone-alt']} />
                            </label>
                            <input type="text" required maxLength="128" name="phone_number" id="phone_number" placeholder="Номер телефона..." onChange={this.handleChange}></input>
                        </div>
                        {(() => {
                            if (this.state.fieldErrors.password) {
                                return (
                                    <div className="errorlist">
                                        {this.state.fieldErrors.password}
                                    </div>
                                )
                            }
                        })()}
                        <div className="fieldWrapper">
                            <label htmlFor="password">
                                <FontAwesomeIcon icon={['fas', 'key']} />
                            </label>
                            <input type="password" required maxLength="128" name="password" id="password" placeholder="Пароль..." onChange={this.handleChange}></input>
                        </div>
                        {(() => {
                            if (this.state.fieldErrors.passwor2) {
                                return (
                                    <div className="errorlist">
                                        {this.state.fieldErrors.password2}
                                    </div>
                                )
                            }
                        })()}
                        <div className="fieldWrapper">
                            <label htmlFor="password2">
                                <FontAwesomeIcon icon={['fas', 'key']} />
                            </label>
                            <input type="password" required maxLength="128" name="password2" id="password2" placeholder="Повторите пароль..." onChange={this.handleChange}></input>
                        </div>
                        <div className="fieldWrapper">
                            <label htmlFor="first_name">
                                <FontAwesomeIcon icon={['fas', 'file-signature']} />
                            </label>
                            <input type="first_name" required maxLength="150" name="first_name" id="first_name" placeholder="Ваше имя..." onChange={this.handleChange}></input>
                        </div>
                        <div className="fieldWrapper">

                            <label htmlFor="last_name">
                                <FontAwesomeIcon icon={['fas', 'file-signature']} />
                            </label>
                            <input type="last_name" required maxLength="150" name="last_name" id="last_name" placeholder="Ваша фамилия..." onChange={this.handleChange}></input>
                        </div>

                        <hr />
                        <p className="auth-logo flex-container align-center" style={{ fontSize: '1.5rem' }}>Выберите фото:</p>
                        <div className="fieldWrapper">
                            <img className="round-thumbnail-200" src={this.state.profile_pic_preview} width='100px' height='100px' alt='NO IMAGE' onClick={this.handleImageClick} id='profile_pic_preview'></img>
                            <input type='file' accept='image/*' name="profile_pic" id="profile_pic" onChange={this.handleChange} style={{ display: 'none' }}></input>
                        </div>
                        <div className="fieldWrapper">
                            <textarea rows="20" cols="35" name="about" id="about" placeholder="  Расскажите о себе" onChange={this.handleChange}></textarea>
                        </div>

                        <div className="submit-btn">
                            <button type="submit">Регистрация</button>
                        </div>
                    </form>
                </div>
            </div>
        )
    }
}

export default RegisterForm;