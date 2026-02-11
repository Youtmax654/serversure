import { Box, Flex, Container, Heading, Text } from '@chakra-ui/react'
import { Smartphone } from 'lucide-react'
import Dashboard from './components/Dashboard'

function App() {
    const ipAddress = 'localhost'

    return (
        <Box minH="100vh" bg="#f7fafc" color="gray.800" fontFamily="'Inter', sans-serif">
            <Container maxW="container.xl" py={8}>
                {/* Header */}
                <Flex justify="space-between" align="center" mb={10} py={4} borderBottom="1px solid" borderColor="gray.200">
                    <Flex align="center" gap={3}>
                        <Box p={2} bg="teal.50" borderRadius="lg" color="teal.500">
                            <Smartphone size={28} />
                        </Box>
                        <Heading size="lg" letterSpacing="tight" color="gray.700">
                            ServerSure <Text as="span" color="gray.400" fontSize="md" fontWeight="medium">Monitor</Text>
                        </Heading>
                    </Flex>
                </Flex>

                {/* Dashboard Content */}
                <Dashboard ipAddress={ipAddress} />

            </Container>
        </Box>
    )
}

export default App
