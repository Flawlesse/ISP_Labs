import React from 'react'
import { axiosInstance, axiosMultipartInstance } from '../../database/axios'
import loadgif from '../../assets/loading.gif'
import defpic from '../../assets/no_pic.jpeg'
import { Redirect, Link } from 'react-router-dom'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import AvailableWalletList from './AvailabeWalletList'

class AccountDetail extends React.Component {
    constructor(props) {
        super(props)
        this.state = {
            username: props.match.params.username,
            first_name: '',
            last_name: '',
            email: '',
            profile_pic: null,
            about: '',
            orders_executed: 0,

            is_admin: false,
            can_edit: false,
            wallets: [],

            loading: true,
            redirect: false,
        }
    }
    componentDidMount() {
        axiosMultipartInstance.get(`/accounts/${this.state.username}`)
            .then((response) => response.data)
            .then((data) => {
                this.setState({ ...data, loading: false })
            })
            .catch((errors) => {
                console.log(errors.data)
                this.setState({ redirect: true })
            })
    }

    handleAccountDelete = () => {
        if (window.confirm("Вы действительно хотите удалить свой аккаунт?")) {
            axiosInstance.delete(`/accounts/${this.state.username}/`)
                .then((response) => response.data)
                .then((data) => {
                    console.log(data)
                    this.setState({ redirect: true })
                })
        }
    }

    render() {
        if (this.state.redirect) {
            return <Redirect to="/"></Redirect>
        }
        if (this.state.loading) {
            return <div className="flex-container align-center"><img src={loadgif}></img></div>
        }


        return (
            <div>
                <div className="flex-container account-detail-section" style={{ marginTop: "110px" }}>
                    <div className="grid-container-outer account-detail">
                        <div className="grid-item flex-container-col align-up" style={{ paddingLeft: "10px", borderRight: "2px solid rgb(63, 62, 62)" }}>
                            <img src={this.state.profile_pic ? this.state.profile_pic : defpic} alt="NO IMAGE" className="round-thumbnail-300" style={{ paddingRight: "10px", paddingBottom: "10px" }} />
                        </div>
                        <div className="grid-item grid-container-inner-account-detail">
                            <div className="grid-item flex-container align-right inverse-center account-action-group">
                                {this.state.can_edit &&
                                    <span>
                                        <Link to={`/accounts/${this.state.username}/update`} className="account-edit-link"><FontAwesomeIcon icon={["fas", "edit"]} /></Link>
                                        <span className="account-delete-link" onClick={this.handleAccountDelete}><FontAwesomeIcon icon={["fas", "trash"]} /></span>
                                    </span>
                                }
                            </div>
                            <div className="grid-item flex-container-col align-center" style={{ borderBottom: "2px solid rgb(63, 62, 62)" }}>
                                <div className="account-content">
                                    <span style={{ fontSize: "3rem", color: "#9e1ce0", paddingLeft: "30px", fontStyle: "italic" }}>{this.state.username}</span>
                                    <p>Имя: {this.state.first_name}</p>
                                    <p>Фамилия: {this.state.last_name}</p>
                                    <p>E-mail: {this.state.email}</p>
                                    <p>Немного о себе:<br />{this.state.about}</p>
                                    <p>Всего выполнено заказов: {this.state.orders_executed}</p>
                                </div>
                            </div>
                            <h2 className="flex-container align-center" style={{ marginBottom: "0" }}>Ваши кошельки:</h2>
                            <AvailableWalletList wallets={this.state.wallets} />
                        </div>
                    </div>
                </div>

            </div>
        )
    }
}

export default AccountDetail;