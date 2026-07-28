import java.util.Objects;

class Auth {
    boolean validate(String token) {
        return Objects.nonNull(token);
    }
}
