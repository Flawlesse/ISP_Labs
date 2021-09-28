import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { Link } from 'react-router-dom'
import { axiosInstance } from '../../database/axios'


const AvailableWalletList = (props) => {
    const wallets = props.wallets

    const handleRemove = (e) => {
        const wallet = e.currentTarget.id
        const name = wallet.split(' ')[0]
        if (window.confirm(`Вы действительно хотите убрать кошелёк ${name} из доступных?`)) {
            axiosInstance.delete(`/wallets/${name}/remove/`)
                .then((response) => response.data)
                .then((data) => {
                    console.log(data);
                    window.location.reload()
                })
                .catch((errors) => {
                    console.log(errors.data);
                })
        }
    }

    return (
        <div className="wallets-container">
            <ul className="wallet-list">
                {
                    wallets.length > 0
                        ?
                        wallets.map((wallet) => (
                            <li key={wallet} className="wallet-item" id={wallet}>
                                <span className="wallet-icon">
                                    <FontAwesomeIcon icon={['fas', 'wallet']} />
                                </span>
                                <span className="wallet-info">
                                    {wallet}
                                </span>
                                <span className="wallet-delete-icon" onClick={handleRemove} id={wallet}>
                                    <FontAwesomeIcon icon={['fas', 'trash-alt']} />
                                </span>
                            </li>
                        ))
                        :
                        <h2>У вас ещё нет кошельков. Добавьте парочку, это удобно.</h2>
                }

                <div className="flex-container align-center" style={{ paddingBottom: "30px" }}>
                    <Link to="/profile/addwallet">
                        <button type="button" className="create-order-btn">
                            Добавить кошелёк
                        </button>
                    </Link>
                </div>
            </ul>
        </div>
    )

}

export default AvailableWalletList;