class UserService {
    constructor(userRepository) {
        this.userRepository = userRepository;
    }

    async delete(id) {
        await this.userRepository.deleteById(id);
        return 'Usuário deletado.';
    }
}

module.exports = UserService;
