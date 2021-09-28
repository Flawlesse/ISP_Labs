import React from 'react';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import defpic from '../../assets/no_pic.jpeg'
import { axiosMultipartInstance } from '../../database/axios.js'
import { Redirect } from 'react-router-dom'

class AccountForm extends React.Component {
    constructor(props) {
        super(props)
        this.state = {
            action: props.action,

            username: props.match.params.username ? props.match.params.username : '',
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
        this.login = props.appLogin
        this.logout = props.appLogout
    }
    componentDidMount() {
        if (this.state.action === "update") {
            axiosMultipartInstance.get(`/accounts/${this.state.username}/`)
                .then((response) => response.data)
                .then((data) => {
                    if (!data.can_edit) {
                        this.setState({ redirect: true })
                    }
                    else {
                        if (data.profile_pic) {
                            // currently data.profile_pic is just URL string
                            this.createFile(data.profile_pic)
                                .then((file) => {
                                    const fileReader = new FileReader()
                                    fileReader.readAsDataURL(file)
                                    const formComponent = this
                                    fileReader.addEventListener("load", function () {
                                        delete data.profile_pic
                                        formComponent.setState((
                                            {
                                                ...data,
                                                profile_pic_preview: this.result,
                                                profile_pic: file,
                                            }
                                        ))
                                    })
                                })
                        }
                        else {
                            this.setState({ ...data })
                        }
                    }
                })
                .catch((errors) => {
                    console.log(errors)
                    this.setState({ redirect: true })
                })
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

    createFile = async (fileURL) => {
        const response = await fetch(fileURL)
        const data = await response.blob()
        const filename = fileURL.split('/').at(-1)
        const metadata = { type: "image/*" }
        const file = new File([data], filename, metadata);
        return file
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
            this.getImgData()
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
        let { profile_pic_preview, fieldErrors, ...postData } = this.state
        let formData = new FormData();
        for (let key in postData) {
            formData.append(key, postData[key]);
        }

        if (this.state.action === "register") {
            axiosMultipartInstance.post('accounts/register/', formData)
                .then((response) => {
                    if (window.confirm("Хотите сразу зайти под новым пользователем?")) {
                        if (this.isLoggedIn) {
                            this.logout()
                        }
                        window.localStorage.setItem('access_token', response.data.token)
                        window.dispatchEvent(new StorageEvent('storage', {
                            storageArea: window.localStorage,
                            key: "access_token",
                            newValue: response.data.token,
                        }))
                        this.login()
                    }

                    this.setState(({
                        redirect: true,
                    }))
                })
                .catch((errors) => {
                    let newFieldErrors = {}
                    console.log(errors.response.data)
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
            formData.delete('password')
            formData.delete('password2')
            axiosMultipartInstance.put(`accounts/${this.state.username}/`, formData)
                .then((response) => {
                    console.log(response.data)
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
        if (this.state.redirect) {
            return <Redirect to='/profile' username={this.state.username}></Redirect>
        }
        return (
            <div className="flex-container-col inverse-cetner" style={{ paddingTop: '10vh' }}>
                <div className="auth-form-wrapper">
                    <div className="auth-logo">
                        {this.state.action === "register" ? "Регистрация" : "Изменить"}
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
                            <input type="text" required maxLength="150" name="username" id="username" placeholder="Имя пользователя..." onChange={this.handleChange} value={this.state.username}></input>
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
                            <input type="email" required maxLength="254" name="email" id="email" placeholder="Эл. почта..." onChange={this.handleChange} value={this.state.email}></input>
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
                            <input type="text" required maxLength="128" name="phone_number" id="phone_number" placeholder="Номер телефона..." onChange={this.handleChange} value={this.state.phone_number}></input>
                        </div>
                        {
                            this.state.action === "register" &&
                            (
                                <div>
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
                                        <input type="password" required maxLength="128" name="password" id="password" placeholder="Пароль..." onChange={this.handleChange} value={this.state.password}></input>
                                    </div>
                                    {(() => {
                                        if (this.state.fieldErrors.password2) {
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
                                </div>
                            )
                        }
                        <div className="fieldWrapper">
                            <label htmlFor="first_name">
                                <FontAwesomeIcon icon={['fas', 'file-signature']} />
                            </label>
                            <input type="first_name" required maxLength="150" name="first_name" id="first_name" placeholder="Ваше имя..." onChange={this.handleChange} value={this.state.first_name}></input>
                        </div>
                        <div className="fieldWrapper">

                            <label htmlFor="last_name">
                                <FontAwesomeIcon icon={['fas', 'file-signature']} />
                            </label>
                            <input type="last_name" required maxLength="150" name="last_name" id="last_name" placeholder="Ваша фамилия..." onChange={this.handleChange} value={this.state.last_name}></input>
                        </div>

                        <hr />
                        <p className="auth-logo flex-container align-center" style={{ fontSize: '1.5rem' }}>Выберите фото:</p>
                        <div className="fieldWrapper">
                            <img className="round-thumbnail-200" src={this.state.profile_pic_preview} width='100px' height='100px' alt='NO IMAGE' onClick={this.handleImageClick} id='profile_pic_preview'></img>
                            <input type='file' accept='image/*' name="profile_pic" id="profile_pic" onChange={this.handleChange} style={{ display: 'none' }}></input>
                        </div>
                        <div className="fieldWrapper">
                            <textarea rows="20" cols="35" name="about" id="about" placeholder="  Расскажите о себе" onChange={this.handleChange} value={this.state.about}></textarea>
                        </div>

                        <div className="submit-btn">
                            <button type="submit">Подтвердить</button>
                        </div>
                    </form>
                </div>
            </div>
        )
    }
}

export default AccountForm;